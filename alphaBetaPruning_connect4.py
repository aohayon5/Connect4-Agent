"""
This is a Connect Four AI implementation that uses Alpha-Beta Pruning for efficient decision-making.
This class includes functions for the heuristic evaluation of the board, move generation, and the alpha-beta algorithm itself.
"""
import copy
import numpy as np

VIC = 10**20    # The value of a winning board (for max/AI) just any large number
LOSS = -VIC     # The value of a losing board (for max/AI) just any large negative number
TIE = 0         # The value of a tie
DEPTH = 4       # Search depth
COMPUTER = 2    # AI player (BLUE)
HUMAN = 1       # Human player (RED)
EMPTY = 0       # Empty cell

# Board dimensions
ROW_COUNT = 6
COLUMN_COUNT = 7

def go(board):
    """
    This is the main function that is called whenever we want the AI to make an intelligent move
    using alpha-beta pruning. It returns the column (0-6 exclusive) where the AI wants to place its piece.
    """
    state = create_state(board)
    
    #AI maximizing player: so alpha starts low, beta starts high
    result = abmax(state, DEPTH, LOSS-1, VIC+1)
    
    # Return the column directly that is chosesn
    return result[1]

def create_state(board):
    """
    The agent needs a state representation that includees values for it to judge it's decisions on
    This is maintained throughout the game and is updated after each move to judge right decisions
    for pruning.
    State format: [board, heuristic_value, whose_turn, empty_cells]
    """
    empty_count = np.count_nonzero(board == 0)

    # When go() is called, it's ALWAYS the COMPUTER's turn (we're asking the AI to make a move)
    # The turn tracking is maintained during the search by make_move()
    whose_turn = COMPUTER

    return [board, 0.00001, whose_turn, empty_count]

def value(s):
    """Returns the heuristic value of state s"""
    return s[1]

def is_finished(s):
    """Returns True if the game ended"""
    return s[1] in [LOSS, VIC, TIE] or s[3] == 0

def is_hum_turn(s):
    """Returns True if it's the human's turn to play"""
    return s[2] == HUMAN

def get_valid_columns(board):
    """Get all valid columns where a piece can be placed"""
    valid_cols = []
    for col in range(COLUMN_COUNT):
        if board[ROW_COUNT - 1][col] == EMPTY:
            valid_cols.append(col)
    return valid_cols

def get_next_row(board, col):
    """Get the next available row in a column"""
    for row in range(ROW_COUNT):
        if board[row][col] == EMPTY:
            return row
    return -1

def check_win(board, piece):
    """
    At a basic level, this method is a check on the simulated board (for any current depth n) if there is a win/loss for either so that it
    does not have to continue searching the board deeper if such terminal states are reached.
    If there is a win within the specified depth, then we would set the heuristic value to VIC or LOSS accordingly.
    """
    
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (board[r][c] == piece and board[r][c+1] == piece and 
                board[r][c+2] == piece and board[r][c+3] == piece):
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (board[r][c] == piece and board[r+1][c] == piece and 
                board[r+2][c] == piece and board[r+3][c] == piece):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (board[r][c] == piece and board[r+1][c+1] == piece and 
                board[r+2][c+2] == piece and board[r+3][c+3] == piece):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (board[r][c] == piece and board[r-1][c+1] == piece and 
                board[r-2][c+2] == piece and board[r-3][c+3] == piece):
                return True
    
    return False

def evaluate_window(window, piece):
    """
    Evaluate a window of 4 positions
    A window is defined as a sequence of 4 consecutive cells in any direction.
    This simply assigns a score based on the number of consecutive same colored chips within a window
    """
    score = 0
    opp_piece = HUMAN if piece == COMPUTER else COMPUTER
    
    piece_count = np.count_nonzero(window == piece)
    empty_count = np.count_nonzero(window == EMPTY)
    opp_count = np.count_nonzero(window == opp_piece)
    
    # Winning move
    if piece_count == 4: 
        score += 100 
    # Good opportunity if AI has potential for 3 in a row
    elif piece_count == 3 and empty_count == 1: 
        score += 5 
    # It's fine to get 2 in a row
    elif piece_count == 2 and empty_count == 2:
        score += 2
    # CRITICAL: Must block opponent's winning threats if they have 3 in a row
    if opp_count == 3 and empty_count == 1:
        score -= 50 
    # Also penalize developing threats from the opponent's perspective
    elif opp_count == 2 and empty_count == 2:
        score -= 3  
    return score

def score_position(board, piece):
    """Score the entire board position, uses the heuristic evaluation of evaluate_window"""
    score = 0
    
    # Score center column - very important for control so increased importance
    center_array = board[:, COLUMN_COUNT//2]
    center_count = np.count_nonzero(center_array == piece)
    score += center_count * 6  # Increased center importance
    
    # Penalty for giving opponent bottom row opportunities early, to prevent 4 turn double threat losses
    # Check if the bottom row has dangerous patterns for opponent
    opp_piece = HUMAN if piece == COMPUTER else COMPUTER
    bottom_row = board[0, :]
    
    # Has to be hardcoded for this threat as mentioned above...
    opp_bottom_count = np.count_nonzero(bottom_row == opp_piece)
    if opp_bottom_count == 2:
        # Check if opponent has 2 pieces with gaps that could lead to double threats
        for c in range(COLUMN_COUNT - 3):
            window = bottom_row[c:c+4]
            if np.count_nonzero(window == opp_piece) == 2 and np.count_nonzero(window == EMPTY) == 2:
                score -= 10  # Penalize allowing double threat setups
    
    # Score Horizontal
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            window = board[r, c:c+4]
            score += evaluate_window(window, piece)
    
    # Score Vertical  
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            window = board[r:r+4, c]
            score += evaluate_window(window, piece)
    
    # Score positive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = np.array([board[r+i][c+i] for i in range(4)])
            score += evaluate_window(window, piece)
    
    # Score negative sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = np.array([board[r+3-i][c+i] for i in range(4)])
            score += evaluate_window(window, piece)
            
    return score

def make_move(s, col):
    """
    Makes a move in column col for the current player in the hypothetical state s and updates the state accordingly.
    """
    board = s[0]
    row = get_next_row(board, col)
    
    if row == -1:
        return  # Invalid move
    
    # Place the piece
    board[row][col] = s[2]
    s[3] -= 1  # One less empty cell
    
    # Switch turns
    s[2] = COMPUTER if s[2] == HUMAN else HUMAN
    
    # Evaluate the position
    if check_win(board, COMPUTER):
        s[1] = VIC
    elif check_win(board, HUMAN):
        s[1] = LOSS
    elif s[3] == 0:
        s[1] = TIE
    else:
        # Heuristic evaluation
        s[1] = score_position(board, COMPUTER) - score_position(board, HUMAN)

def get_next(s):
    """Returns a llist of all possible next states from state s"""
    next_states = []
    valid_cols = get_valid_columns(s[0])
    
    # Order columns by distance from center for better pruning
    # Center columns are usually better, so check them first heuristically
    center = COLUMN_COUNT // 2
    ordered_cols = sorted(valid_cols, key=lambda x: abs(x - center))
    
    for col in ordered_cols:
        state_copy = copy.deepcopy(s)
        make_move(state_copy, col)
        # Store the column that was played
        state_copy.append(col)
        next_states.append(state_copy)
    
    return next_states

def abmax(s, d, a, b):
    """
    Alpha-Beta maximizer (AI's turn)
    s = the state (max's turn)
    d = max depth of search
    a, b = alpha and beta
    returns [v, col]: v = state value, col = recommended column
    """
    if d == 0 or is_finished(s):
        return [value(s), 0]
    
    v = float("-inf")
    best_col = 0
    next_states = get_next(s)
    
    for state in next_states:
        col_played = state[-1] if len(state) > 4 else 0
        tmp = abmin(copy.deepcopy(state[:4]), d-1, a, b)
        
        if tmp[0] > v:
            v = tmp[0]
            best_col = col_played
        
        if v >= b:
            return [v, col_played]
        
        if v > a:
            a = v
    
    return [v, best_col]

def abmin(s, d, a, b):
    """
    Alpha-Beta minimizer (Human's turn)
    s = the state (min's turn)
    d = max depth of search
    a, b = alpha and beta
    returns [v, col]: v = state value, col = recommended column
    """
    if d == 0 or is_finished(s):
        return [value(s), 0]
    
    v = float("inf")
    best_col = 0
    next_states = get_next(s)
    
    for state in next_states:
        col_played = state[-1] if len(state) > 4 else 0
        tmp = abmax(copy.deepcopy(state[:4]), d-1, a, b)
        
        if tmp[0] < v:
            v = tmp[0]
            best_col = col_played
        
        if v <= a:
            return [v, col_played]
        
        if v < b:
            b = v
    
    return [v, best_col]
