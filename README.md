# AI For Connect 4
Connect 4 artificial intelligence which uses the minimax algorithm to assess all possible outcomes up to the given search depth and calculates the best possible move using this data. The AI uses alpha beta pruning to narrow down its search options without sacrificing its performance in order to speed up the search process. Finally temporary transposition table is implemented which stores the board positions of the calculated outcomes alongside the depth of the calculations and the scores given to each board. Using the transposition table, iterative deepening can be introduced which means the AI will progressively search deeper as the game goes on as there will be fewer possible moves and a larger transposition table.


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

The minimax algorithm, when used naively, is very slow and inefficient as it explores all possible outcomes up to certain depth meaning with each depth the search time increases 7x. Alpha beta pruning significantly reduces the search time by eliminating branches of the search that will never be explored as it is undesirable for either the AI, or the player, and so the minimax will never have returned a final value from that branch. The nature of the algorithm means if the best move is found early in the search, more beaches can be disregarded. Therefore the searching algorithm is altered to search moves form the centre column first, them spread the search outwards to neighbouring columns, as the best move is more likely to be nearer to the centre.

## Scoring Function

### Basic Scoring System

The AI uses a scoring function to assess board positions in order to implement the minimax algorithm. After testing different values, the following were found to work the best:
```
3 AI and 1 EMPTY  =====>   +5
2 AI and 2 EMPTY  =====>   +2

3 PLAYER and 1 EMPTY  ==>  -5
2 PLAYER and 2 EMPTY  ==>  -2
```
Alongside this basic scoring system, the odd-even strategy was implemented to more accurately calculate the value of a given position so the AI can improve its decision making.

### Odd-Even Strategy

The odd-even strategy dictates that is is favourable for the odd player to have a potential win with an empty position which completes the win on an odd row, with the opposite true for the even player. The odd player is the player that starts first and vice versa for the even player. This is because the other player will eventually be forced to play their coin in the column which gives their opponent the win if the board becomes full. Therefore the lower down the empty space is, the better, and the power the strategy means it must be scored highly:
```
Odd-Even for AI  =======>  Distance from top * 100
Odd-Even for PLAYER  ===>  Distance from top * -100
```

## Graphical UI

The Connect 4 board is dealt with as a 2D numpy array, in order to easily add coins and give to the minimax algorithm to assess. This is converted into a graphical representation of the board using the pygame module. The player can use the mouse to choose where to drop their coin, and after every move the graphical representation of the board is updated, and an indication of where the AI dropped its coin is displayed. When a player has won, the 4 consecutive coins will be indicated and the program will close.
