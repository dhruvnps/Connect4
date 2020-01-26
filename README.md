# AI For Connect 4
A Connect 4 artificial intelligence which uses the minimax algorithm and alpha beta pruning to search for the possible best move. A transposition table is incorporated to store calculations and iterative deepening is used to make the AI progressively better as the game goes on when there are less possible outcomes. The pygame module is used for a graphical user interface in which the player can compete with the AI on a 6 x 7 board displayed on the screen. The difficulty of the AI can be adjusted by changing the time available to the AI.

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

The minimax algorithm, when used naively, is very slow and inefficient as it explores all possible outcomes up to certain depth meaning with each depth the search time increases 7x. Alpha beta pruning significantly reduces the search time by eliminating branches of the search that will never be explored as it is undesirable for either the AI, or the player, and so the minimax will never have returned a final value from that branch. The nature of the algorithm means if the best move is found early in the search, more branches can be disregarded. Therefore the searching algorithm is altered to search moves form the centre column first, them spread the search outwards to neighbouring columns, as the best move is more likely to be nearer to the centre.

## Scoring Function

### Basic Scoring System

The AI uses a scoring function to assess board positions in order to implement the minimax algorithm. After testing different values, the following were found to work the best:
```
3 AI and 1 EMPTY  ======>  +5
2 AI and 2 EMPTY  ======>  +2

3 PLAYER and 1 EMPTY  ==>  -5
2 PLAYER and 2 EMPTY  ==>  -2
```
Alongside this basic scoring system, the odd-even strategy was implemented to more accurately calculate the value of a given position so the AI can improve its decision making.

### Odd-Even Strategy

The odd-even strategy dictates that is is favourable for the odd player to have a potential win with an empty position which completes the win on an odd row, with the opposite true for the even player. The odd player is the player that starts first and vice versa for the even player. This is because when the board becomes full the other player will be forced to play their coin in the column that will give the opponent the win. Therefore the lower down the empty space is, the better. The power the strategy means it must be scored highly:
```
Odd-Even for AI  =======>  Distance from top * 100
Odd-Even for PLAYER  ===>  Distance from top * -100
```

### Winning Move

The winning move must be given ultimate value as it is the aim of the game.
```
Winning Move  ==========>  +1000000
Loosing Move  ==========>  -1000000
```

The AI can be optimised by anticipating a win when the board is in a position in which any one player can win the game in the next move. This effectively means that a depth 4 AI can peak into what will happen at depth 5, and can prevent a loss or push to a win.
```
Anticiapted Win  =======>  +100000
Anticiapted Loss  ======>  -100000
```
This value is 10x less than the value give to a win, because is must be much greater than all other board positions, however a win/loss is still prioritised over an imminent win/loss as the AI must not opt for a potential win and loose the game as a result.

## Graphical User Interface

The Connect 4 board is dealt with as a 2D numpy array, in order to easily add coins and give to the minimax algorithm to assess. This is converted into a graphical representation of the board using the pygame module. The player can use the mouse to choose where to drop their coin, and after every move the graphical representation of the board is updated, and an indication of where the AI dropped its coin is displayed. When a player has won, the 4 consecutive coins will be indicated and the program will close.

## Further Optimisations

### Transposition table

The transposition table uses zobrist hashing to store hash values of board positions calculated during the game to save the AI from starting from scratch every time it is called to calculate the best move. The transposition stores the hash of the board, the score of the boars, and the calculation depth that has resulted in the score. The transposition table is referred to every time the minimax algorithm is assessing a board, and if the board hash is in the table, and the calculation depth is greater than or equal to the depth of calculation the minimax algorithm must perform, the score stored in the table is used and the calculation doesn’t need to be done. If the table does not contain a hash, or the table contains a hash with a lower corresponding depth than the one calculated, the entry in the table is (over)written be the new calculation. This way the efficiency of the AI is improved significantly.

### Iterative Deepening

Using the introduction of the transposition table, iterative deepening can be implemented. Therefore, instead of limiting the depth of the search, the time available to the AI can be the limiting factor. The AI will iterative increase the depth of the search until the time available is up, at which point the AI is terminated and the move returned by the highest depth that could be calculated in the given time is used as the final move. The calculations made by lower depth iterations are saved in the transposition table, so as the depth is increased, the minimax can build upon the previous calculations instead of repeating them. Iterative deepening allows the depth of the search to increase as the game progresses and therefore the AI will become better as the game goes on.

## Adjustable Parameters

The time available to the AI can be adjusted to any integer value. A value of 1 is relatively easy to beat when the AI is playing second, and averages a depth of 5 at the start of the game. A value of 2 to 5 is significantly harder to beat and averages a depth of 6 to 7 at the start, with the depth increasing significantly as the game progresses. A value of more that 6 is very difficult to beat when the AI plays second, and almost impossible beat when the AI plays first, averaging a depth of 7 to 8 at the start, and reaching depths of over 10 after a few moves.
```
# maximum seconds AI can take
AI_TIME = 6
```

The play order can be adjusted to give the first move to the PLAYER or to the AI. The order of play is randomised by default.
```
PLAY_ORDER = [PLAYER, AI]

# PLAY_ORDER.reverse()
random.shuffle(PLAY_ORDER)
```

