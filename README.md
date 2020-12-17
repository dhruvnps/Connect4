# AI For Connect 4
> A Connect 4 AI which uses the minimax algorithm and alpha beta pruning to search for the possible best move. A transposition table is incorporated storing previous calculations and iterative deepening is used to make the AI search progressively deeper as the transposition table becomes larger. The pygame module is used for the GUI in which the player can compete with the AI on a 6 x 7 board. The difficulty of the AI can be adjusted by changing the time available to the AI.

## Usage

To run the script vs AI:
```console
$ python Connect4_AI.py
```
See the section on [adjustable parameters](#adjustable-parameters) to change behaviour of the AI

The transposition and zobrists tables are already present with game data.
To reset the tables:
```console
$ python Cache_Init.py
```
or, delete the ```cachetable.pickle``` and ```zobtable.pickle``` files.
Running the AI script will automatically check for these files and run the ```Cache_Init.py``` script if the files are not found.

To run the 2 player script:
```console
$ python Connect4_Basic.py
```

### Dependencies

The following external modules are used
-   [pygame](https://pypi.org/project/pygame)
-   [numpy](https://pypi.org/project/numpy)

Commands for installation of pygame 2.0 and numpy
```console
$ pip install pygame
$ pip install numpy
```

## Searching algorithms

### Minimax

> This AI uses the minimax algorithm to search for all possible board outcomes and returns the best move which will result in the best scoring board position if the AI always plays the move maximising its chance of winning and the opponent player always plays the move minimising the AI’s chance of winning. The minimax will go down each possible board position and recursively score that board position using the minimax algorithm at a lower depth, until all board positions and their scores up to a given depth are calculated. The AI will then return the best board position if it is the AI’s move, and return the worst board position if it is the player’s move. The algorithm will therefore finally return the best move to play at the current moment to maximise the score of the eventual board position if the player plays the best moves as expected.

### Alpha Beta Pruning

> The minimax algorithm, when used naively, is slow and inefficient as it explores all possible outcomes up to certain depth, meaning with each depth the search time increases 7x. Alpha beta pruning significantly reduces the search time by eliminating branches of the search that will never be explored as it is undesirable for either the AI, or the player, and so the minimax will never have returned a final value from that branch. The nature of the algorithm means if the best move is found early in the search, more branches can be disregarded. Therefore the searching algorithm is altered to search moves form the centre column first, then spread the search outwards to neighbouring columns, as the best move is more likely to be nearer to the centre.

## Scoring Function

### Basic Scoring System

> The AI uses a scoring function to assess board positions in order to implement the minimax algorithm. After testing different values, the following were found to work the best:
```
3 AI and 1 EMPTY  ------>  +5
2 AI and 2 EMPTY  ------>  +2

3 PLAYER and 1 EMPTY  -->  -5
2 PLAYER and 2 EMPTY  -->  -2
```
> Alongside this basic scoring system, the odd-even strategy was implemented to more accurately calculate the value of a given position so the AI can improve its decision making.

### Odd-Even Strategy

> The odd-even strategy dictates that is is favourable for the odd player to have a potential win with an empty position which completes the win on an odd row, with the opposite true for the even player. The odd player is the player that starts first and vice versa for the even player. This is because when the board becomes full the other player will be forced to play their coin in the column that will give the opponent the win. Therefore the lower down the empty space is, the better. The power the strategy means it must be scored highly:
```
Odd-Even for AI  ------->  Distance from top * 100
Odd-Even for PLAYER  --->  Distance from top * -100
```

### Winning Move

> The winning move must be given ultimate value as it is the aim of the game.
```
Winning Move  ---------->  +1000000
Loosing Move  ---------->  -1000000
```

> The AI can be optimised by anticipating a win when the board is in a position in which any one player can win the game in the next move. This effectively means that a depth 4 AI can peak into what will happen at depth 5, and can prevent a loss or push to a win.
```
Anticiapted Win  ------->  +100000
Anticiapted Loss  ------>  -100000
```
> This value is 10x less than the value give to a win, because is must be much greater than all other board positions, however a win/loss is still prioritised over an imminent win/loss as the AI must not opt for a potential win and loose the game as a result.

## Further Optimisations

### Transposition table

> The transposition table uses zobrist hashing to store hash values of board positions calculated during the game to save the AI from starting from scratch every time it is called to calculate the best move. The transposition table stores the hash of the board, the score of the board, and the calculation depth that has resulted in the score. The transposition table is referred to every time the minimax algorithm is assessing a board, and if the board hash is in the table and the calculation depth is greater than or equal to the depth of calculation the minimax algorithm must perform, the score stored in the table is used and the calculation doesn’t need to be done. If the table does not contain a hash, or the table contains a hash with a lower corresponding depth than the one calculated, the entry in the table is (over)written as the new calculation. The calculations made in previous games are saved in the transposition table so the minimax can build upon the previous calculations instead of repeating them in future games.

### Iterative Deepening

> Using the introduction of the transposition table, iterative deepening can be implemented. Instead of limiting the depth of the search, the time available to the AI can be the limiting factor. The AI will iterative increase the depth of the search until the time available is up, at which point the AI is terminated and the move returned by the highest depth that could be calculated in the given time is used as the final move.

## Adjustable Parameters

The time available to the AI in seconds can be adjusted to any integer value. A higher time value means the AI will achieve a higher depth of calculation.
```python
# maximum seconds AI can take
AI_TIME = 6
```

This can be switched to true to train the AI by making it playing itself. This will improve the AI by increasing the number or boards stored in the transposition table.
```python
AI_VS_AI = False
```

The play order can be adjusted to give the first move to the PLAYER or to the AI. The order of play is randomised by default.
```python
PLAY_ORDER = [PLAYER, AI]

# PLAY_ORDER.reverse()
random.shuffle(PLAY_ORDER)
```

