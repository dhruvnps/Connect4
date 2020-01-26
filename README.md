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

## Searching algorithm

# Minimax

abc

# Alpha Beta Pruning

abc


## Graphical UI
