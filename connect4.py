"""
CONNECT FOUR WITH AI
Fully integrated board game with Terminal UI and AI using Alpha-Beta Pruning
This script allows a human player to play Connect Four against an AI opponent.
The AI uses the alpha-beta pruning algorithm for efficient decision-making.
@See documentation .md file for more details.
"""

import copy
import numpy as np
import random

# Colors the board if termcolor is installed, but let's you play without it too.
try:
    from termcolor import colored
except ImportError:
    def colored(text, color):
        return text
import alphaBetaPruning_connect4 as ai_engine

# globals
ROW_COUNT = 6
COLUMN_COUNT = 7
# X is human, O is AI
RED_CHAR = colored('X', 'red')
BLUE_CHAR = colored('O', 'blue')

EMPTY = 0
RED_INT = 1
BLUE_INT = 2


# Board functions
def create_board():
    """Create board initialized to all zeros with numpy for easy access and efficiency"""
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board


def drop_chip(board, row, col, chip):
    """place the chip on the board in the specified row and column"""
    board[row][col] = chip


def is_valid_location(board, col):
    """just checks if I can place the chip here"""
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    """gives lowest empty row to leverage gravity effect"""
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    """just prints the board in the terminal"""
    print(" 1 2 3 4 5 6 7 \n" "|" + np.array2string(np.flip(np.flip(board, 1)))
          .replace("[", "").replace("]", "").replace(" ", "|").replace("0", "_")
          .replace("1", RED_CHAR).replace("2", BLUE_CHAR).replace("\n", "|\n") + "|")

def game_is_won(board, chip):
    """Check if there is a win after "chip" is placed"""
    winning_Sequence = np.array([chip, chip, chip, chip])
    # Check horizontal sequences
    for r in range(ROW_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[r, :]))):
            return True
    # Check vertical sequences
    for c in range(COLUMN_COUNT):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board[:, c]))):
            return True
    # Check positively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, board.diagonal(offset)))):
            return True
    # Check negatively sloped diagonals
    for offset in range(-2, 4):
        if "".join(list(map(str, winning_Sequence))) in "".join(list(map(str, np.flip(board, 1).diagonal(offset)))):
            return True
    return False


def get_valid_locations(board):
    '''Get all valid columns where a piece can be placed so we know what to evaluate, or if we don't need that column at all'''
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations



#Strategies: Random or AI

def MoveRandom(board, color):
    """This method embodies the random agents strategy; simple: just choose a random column"""
    valid_locations = get_valid_locations(board)
    column = random.choice(valid_locations)   
    row = get_next_open_row(board, column)
    drop_chip(board, row, column, color)



# Heuristics the AI uses to play the game below, based on the depth, checks the option at every point. So would be on a board with 7 columns: 7^depth options without
# pruning, but with it cuts down options significantly and allows us to look 4 moves ahead with reasonable time


def should_win(board, piece):
    """Helper method: If the AI can win this turn it should"""
    for col in get_valid_locations(board):
        temp_board = copy.deepcopy(board)
        row = get_next_open_row(temp_board, col)
        drop_chip(temp_board, row, col, piece)
        if game_is_won(temp_board, piece):
            return col
    return None

def should_block(board, piece):
    """Helper method: If AI can block this turn it should"""
    opponent = RED_INT if piece == BLUE_INT else BLUE_INT
    for col in get_valid_locations(board):
        temp_board = copy.deepcopy(board)
        row = get_next_open_row(temp_board, col)
        drop_chip(temp_board, row, col, opponent)
        if game_is_won(temp_board, opponent):
            return col
    return None

def MoveAI(board, color):
    """
    Helper method: AI move using alpha-beta pruning
    This is the main improvement over MoveRandom and kicks in if there is no simple win or block on the current move which is included for simplification.
    """
    print("AI is thinking...")
    
    # Use the alpha-beta pruning engine to get the best column
    best_col = ai_engine.go(board)
    
    row = get_next_open_row(board, best_col)
    drop_chip(board, row, best_col, color)
    print(f"AI chooses column {best_col + 1}")
        
        
def MoveSmartAI(board, color):
    """
    This method essentially embodies the AI's strategy:
    1. Check if it can win this turn and do so.
    2. Check if it needs to block the opponent from winning next turn and do so
    3. Otherwise, use alpha-beta pruning to determine the best move.
    
    PERSONAL SIDE NOTE: in retrospect the 1st two checks are external from the alpha-beta pruning and aren't really necessary since it would find the right
    moves anyways, and it does only speed efficiency in cases where the next move is an immediate win or block, but fun to include and does speed things up more if only slightly.
    """
    # First priority: Win if possible
    win_col = should_win(board, color)
    if win_col is not None:
        row = get_next_open_row(board, win_col)
        drop_chip(board, row, win_col, color)
        print(f"AI wins by playing column {win_col + 1}!")
        return
    
    # Second priority: Block ALL opponent's wins (check thoroughly)
    opponent = RED_INT if color == BLUE_INT else BLUE_INT
    blocks_needed = []
    for col in get_valid_locations(board):
        temp_board = copy.deepcopy(board)
        row = get_next_open_row(temp_board, col)
        drop_chip(temp_board, row, col, opponent)
        if game_is_won(temp_board, opponent):
            blocks_needed.append(col)
    
    # If there's only one threat, block it
    if len(blocks_needed) == 1:
        col = blocks_needed[0]
        row = get_next_open_row(board, col)
        drop_chip(board, row, col, color)
        print(f"AI blocks opponent's win at column {col + 1}!")
        return
    
    # Otherwise use alpha-beta pruning for best move
    MoveAI(board, color)


def main():
    """Main game loop execution"""
    board = create_board()
    print("\n" + "="*50)
    print("CONNECT FOUR WITH AI (Alpha-Beta Pruning)")
    print("="*50)

    # Ask player if they want to go first or second
    player_choice = input("Do you want to play first or second? (1/2): ")
    while player_choice not in ['1', '2']:
        player_choice = input("Invalid choice. Please enter 1 for first or 2 for second: ")

    player_goes_first = (player_choice == '1')

    # Player is always RED (X), AI is always BLUE (O) to match AI engine constants
    # We just change who goes first by adjusting the turn counter
    turn = 0 if player_goes_first else 1

    print("You are RED (X), AI is BLUE (O)")
    if player_goes_first:
        print("You will play first!")
    else:
        print("AI will play first!")
    print("The AI uses minimax with alpha-beta pruning")
    print("="*50 + "\n")

    print_board(board)
    game_over = False

    while not game_over:
        if turn % 2 == 0:
            # Human player (RED)
            col = int(input("RED please choose a column(1-7): "))
            while col > 7 or col < 1:
                col = int(input("Invalid column, pick a valid one: "))
            while not is_valid_location(board, col - 1):
                col = int(input("Column is full. pick another one..."))
            col -= 1

            row = get_next_open_row(board, col)
            drop_chip(board, row, col, RED_INT)

        else:
            # AI player (BLUE) - using smart AI instead of random
            MoveSmartAI(board, BLUE_INT)

        print_board(board)

        # Check for game over conditions
        if game_is_won(board, RED_INT):
            game_over = True
            print("\n" + "="*50)
            print(colored("RED (YOU) WIN! Congratulations!", 'red'))
            print("="*50)
        elif game_is_won(board, BLUE_INT):
            game_over = True
            print("\n" + "="*50)
            print(colored("BLUE (AI) WINS! Better luck next time!", 'blue'))
            print("="*50)
        elif len(get_valid_locations(board)) == 0:
            game_over = True
            print("\n" + "="*50)
            print(colored("IT'S A DRAW!", 'yellow'))
            print("="*50)

        turn += 1

    print("\nThanks for playing!")

# Test performance against random agent included for evaluation purposes
def ai_vs_random(num_games):
    """Test AI against randomized agents to evaluate performance"""
    ai_wins = 0
    random_wins = 0
    draws = 0
    
    print(f"\nTesting AI vs Random for {num_games} games...")
    print("Random plays first (RED), AI plays second (BLUE)")
    
    for game in range(num_games):
        board = create_board()
        game_over = False
        turn = 0
        
        while not game_over:
            if turn % 2 == 0:
                # Random plays as RED (goes first, like human)
                MoveRandom(board, RED_INT)
            else:
                # AI plays as BLUE (goes second, always)
                best_col = ai_engine.go(board)
                # No need to check if None - should always return valid column now
                row = get_next_open_row(board, best_col)
                drop_chip(board, row, best_col, BLUE_INT)
            
            if game_is_won(board, RED_INT):
                random_wins += 1
                game_over = True
            elif game_is_won(board, BLUE_INT):
                ai_wins += 1
                game_over = True
            elif len(get_valid_locations(board)) == 0:
                draws += 1
                game_over = True
            turn += 1
    
    print(f"Results: AI wins: {ai_wins}, Random wins: {random_wins}, Draws: {draws}")
    print(f"AI win rate: {(ai_wins/num_games)*100:.1f}%")

if __name__ == "__main__":
    # Main game
    main()
    
    # Optional: Test AI performance
    test_mode = input("\nWould you like to see AI vs Random test results? (0/number of games): ")
    if test_mode.isdigit() and int(test_mode) != 0:
        ai_vs_random(int(test_mode))