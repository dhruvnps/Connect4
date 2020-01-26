# AI for Connect 4
Connect 4 artificial intelligence which uses the minimax algorithm to access all possible outcomes up to the given search depth and calculates the best possible move using this data. The AI uses alpha beta pruning to narrow down its search options without sacrificing its performance in order to speed up the search process. Finally temporary transposition table is implemented which stores the board positions of the calculated outcomes alongside the depth of the calculations and the scores given to each board. Using the transposition table, iterative deepening can be introduced which means the AI will progressively search deeper as the game goes on as there will be fewer possible moves and a larger transposition table.


## Prerequisites

The following modules are used by this program
```
pygame
numpy
math
random
time
signal
```
Commands for installation of pygame 2.0 and numpy
```
pip install pygame==2.0.0.dev6
pip install numpy
```


## Searching algorithms

### Minimax

This AI uses the minimax algorithm to search for all possible board outcomes and returns the best move which will result in the best scoring board position if the AI always plays the move maximising its chance of winning and the opponent player always plays the move minimising the AI’s chance of winning. The minimax will go down each possible board position and recursively score that board position using the minimax algorithm at a lower depth, until all board positions and their scores up to a given depth are calculated. The AI will then return the best board position if it is the AI’s move, and return the worst board position if it is the player’s move. The algorithm will therefore finally return the best move to play at the current moment to maximise the score of the eventual board position if the player plays the best moves as expected.

### Alpha Beta Pruning

abc


## Graphical UI
