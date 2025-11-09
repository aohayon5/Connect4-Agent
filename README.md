# Connect4 Agent

A Connect Four implementation featuring an AI opponent that uses minimax with alpha-beta pruning to facilitate strategically impactful decisions. The AI looks several moves ahead using advanced heuristic evaluation, winning the vast majority of games against random opponents while maintaining fast performance.

## Example Game

AI wins by playing column 2!
 1 2 3 4 5 6 7
|_|_|_|_|_|_|_|
|_|_|X|X|_|_|_|
|_|O|X|O|_|_|_|
|_|O|O|X|_|_|_|
|_|X|X|O|O|_|_|
|O|X|X|X|O|O|_|

==================================================
BLUE (AI) WINS! Better luck next time!
==================================================


 1 2 3 4 5 6 7 
|X|X|O|O|_|O|_|
|X|O|X|X|X|X|_|
|O|X|X|O|O|O|_|
|O|O|O|X|O|X|_|
|O|O|X|O|X|O|X|
|X|O|X|X|X|O|X|

==================================================
RED (YOU) WIN! Congratulations!
==================================================

## Features

- **Alpha-Beta Pruning**: Minimax algorithm with alpha-beta pruning for efficient game tree exploration
- **Strategic Heuristics**: Advanced board evaluation including center control, threat detection, and pattern matching
- **Adaptive Gameplay**: Balances offensive and defensive strategies based on board state
- **Player Choice**: Select whether to play first or second at the start of each game
- **Fast Performance**: <1 second per move at depth 4
- **Colored Terminal UI**: Visual board representation with colored pieces (requires optional `termcolor` package)

## Installation

### Requirements
- Python 3.x
- NumPy (required)
- termcolor (optional, for colored output)

### Setup
```bash
pip install numpy termcolor
```

## How to Run

Run the main game:
```bash
python connect4.py
```

At the start, you'll be prompted to choose whether to play first or second. The AI will adapt to play as the corresponding opponent.

## Project Structure

- **connect4.py** - Main game engine with terminal UI, game logic, and player interaction
- **alphaBetaPruning_connect4.py** - AI decision engine implementing minimax with alpha-beta pruning
- **README.md** - This file

## How the Algorithm Works

### Minimax with Alpha-Beta Pruning

The AI uses a minimax decision-making process enhanced with alpha-beta pruning:
- **`abmax()`**: Maximizes the AI's advantage
- **`abmin()`**: Minimizes from the opponent's perspective (simulates opponent's best moves)
- **Alpha-Beta Pruning**: Eliminates branches where `alpha ≥ beta`, significantly reducing the number of positions evaluated
- **Search Depth**: Set to 4 moves ahead to balance strategic strength with computation speed

The algorithm simulates future game states at each depth level, evaluating boards using heuristics and choosing the move that maximizes the AI's winning potential while minimizing the opponent's opportunities.

### Board Evaluation Heuristics

The `score_position()` function evaluates board states using multiple strategic factors:

#### Center Column Priority (+6 points per piece)
The center column is the most strategically valuable position. Pieces placed in the center can connect in more directions than edge pieces, making them critical for both offensive and defensive play. This heuristic helps the AI establish strong positioning early and maintain control throughout the game.

#### Pattern Matching
All 4-cell windows (horizontal, vertical, and diagonal) are scored for potential:
- **4-in-a-row**: +100 points (winning position)
- **3-in-a-row + 1 empty**: +5 points (immediate winning opportunity)
- **2-in-a-row + 2 empty**: +2 points (building potential)
- **Opponent 3-in-a-row + 1 empty**: -50 points (critical defensive priority)
- **Opponent 2-in-a-row + 2 empty**: -3 points (defensive awareness)

#### Bottom Row Protection (-10 penalty)
Prevents the opponent from clustering pieces in consecutive bottom-row columns early in the game. This heuristic blocks a strategic advantage that would be difficult to counter later, as controlling adjacent bottom squares creates multiple upward connection opportunities.

### Strategic Optimizations

1. **Immediate Win/Block Detection**: `should_win()` and `should_block()` handle obvious moves instantly without requiring deep search
2. **Move Ordering**: Evaluates center columns first for better pruning efficiency
3. **Double Threat Awareness**: Independently evaluates all threats, making double threats doubly important
4. **Adaptive Strategy**: Naturally aggressive when advantageous, defensive when necessary - prioritizes blocking opponent's 3-in-a-row over connecting its own 2-in-a-row

## Performance

### vs. Random Opponents
- **Win Rate**: Wins the vast majority of games (typically >99% in testing)
- **Reason**: The AI almost always identifies winning moves, blocks critical threats, and looks 4 moves ahead while random agents look 0 moves ahead
- **Note**: In rare cases (~1% or less), random moves can accidentally create "forced game" endgame scenarios where both players have only one valid response per turn, and the outcome depends on move sequence rather than heuristics. The AI's depth limitation may not foresee these positions.

### vs. Skilled Players
- **Performance**: Strong competitive play, rarely loses
- **Limitations**:
  - May lose in "forced game" scenarios where the final moves create a sequence of forced responses, and whoever must place first in a losing position loses
  - Depth limitation (4 moves) can be exploited by expert players using advanced multi-step trap sequences
  - Connect Four is a solved game, so perfect play from the first player guarantees a win

### Speed
- **< 1 second per move** at depth 4

## Testing

The project includes an AI vs. Random testing mode to verify performance:
```bash
python connect4.py
# After the game, enter the number of test games when prompted
```

## Technical Implementation

- **NumPy** for efficient board operations and array manipulation
- **Deep Copy** for simulating future board states without affecting the actual game
- **Optimized Search**: Terminates early for forced moves, evaluates strategic positions first
- **Robust Win Detection**: Checks all horizontal, vertical, and diagonal sequences

## Why It Almost Always Beats Random Opponents

1. Prioritizes blocking winning threats (-50 penalty makes blocking highest priority)
2. Looks 4 moves ahead vs. random's 0 moves
3. Strategic positioning through center control and pattern recognition
4. Identifies immediate winning opportunities
5. Actively builds winning connections while disrupting opponent patterns

**Rare Exception**: In uncommon forced endgame scenarios where both players have only one legal move per turn, heuristics cannot distinguish between moves. The AI's depth-4 search may not foresee these positions far enough in advance, potentially leading to a loss if the move sequence is unfavorable.

---

**Note**: Connect Four is a solved game. First player can force a win with perfect play. This AI provides strong strategic gameplay but is not perfect-play optimal due to computational constraints.
