import pygame
import numpy as np
import math
import random
import time

AI_DEPTH = 6

ROW_LEN, COLUMN_LEN = 6, 7
BOARD = np.zeros((ROW_LEN, COLUMN_LEN))

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (217, 60, 79)
YELLOW = (250, 150, 60)

EMPTY = 0
PLAYER = 1
AI = 2

PLAY_ORDER = [PLAYER, AI]
# random.shuffle(PLAY_ORDER)

SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 3)

WIN_HEIGHT = (ROW_LEN + 1) * SQUARESIZE
WIN_WIDTH = COLUMN_LEN * SQUARESIZE

HIGH_VALUE = 1000000


def drop_coin(column, coin, board_input):
    for row in range(ROW_LEN):
        if board_input[row][column] == EMPTY:
            board_input[row][column] = coin
            return True
    return False


def draw_board(win):
    win.fill(WHITE)
    pygame.draw.rect(win, BLACK, (0, SQUARESIZE, WIN_WIDTH, WIN_HEIGHT))

    for column in range(COLUMN_LEN):
        for row in range(ROW_LEN):
            color = WHITE
            if BOARD[row][column] == PLAYER:
                color = RED
            elif BOARD[row][column] == AI:
                color = YELLOW
            pygame.draw.circle(win, color, (int((column + 0.5) * SQUARESIZE), int((ROW_LEN - (row - 0.5)) * SQUARESIZE)), RADIUS)


def draw_mouse(win, mouse_x, turn):
    if turn == PLAYER:
        color = RED
    else:
        color = YELLOW
    pygame.draw.circle(win, color, (mouse_x, int(SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


def is_game_won(board):
    scan = scan_fours(board)
    if [PLAYER for _ in range(4)] in scan[0]:
        return PLAYER
    elif [AI for _ in range(4)] in scan[0]:
        return AI
    return 0


# returns a list with all possible windows of 4
def scan_fours(board):
    scan = []
    locations = []

    for row in range(ROW_LEN):
        for column in range(COLUMN_LEN):
            # adds row to scan
            if column + 3 < COLUMN_LEN:
                scan.append([board[row][column + i] for i in range(4)])
                # row index for every coin of scan for odd-even strategy
                locations.append([(row, column + i) for i in range(4)])

            # adds column to scan
            if row + 3 < ROW_LEN:
                scan.append([board[row + i][column] for i in range(4)])
                # odd-even strategy cannot be applied for rows
                locations.append((0, 0) for i in range(4))

            # adds negative diagonal to scan
            if row - 3 >= 0 and column + 3 < COLUMN_LEN:
                scan.append([board[row - i][column + i] for i in range(4)])
                # row index for every coin of scan for odd-even strategy
                locations.append([(row - i, column + i) for i in range(4)])

            # adds positive diagonal to scan
            if row + 3 < ROW_LEN and column + 3 < COLUMN_LEN:
                # row index for every coin of scan for odd-even strategy
                scan.append([board[row + i][column + i] for i in range(4)])
                locations.append([(row + i, column + i) for i in range(4)])

    return scan, locations


# //----------------------------------------AI_START----------------------------------------//


def score_position(board):
    score = 0
    scan, locations = scan_fours(board)

    for i in range(len(scan)):
        # score positively for combinations made by AI
        if scan[i].count(AI) == 3 and scan[i].count(EMPTY) == 1:
            score += 5

            # use odd-even strategy for AI
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, AI, empty_location, 100)

        if scan[i].count(AI) == 2 and scan[i].count(EMPTY) == 2:
            score += 2

        # score negatively for combinations made by PLAYER
        if scan[i].count(PLAYER) == 3 and scan[i].count(EMPTY) == 1:
            score -= 4

            # block odd-even strategy from PLAYER
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, PLAYER, empty_location, -80)

    # score positively for AI coins in center column
    center_column = [board[i][COLUMN_LEN // 2] for i in range(ROW_LEN)]
    score += center_column.count(AI)

    return score


def odd_even_strategy(board, coin, location, score_bonus):
    row, column = location
    if row > 0:
        # rewards applying the odd-even strategy
        if row % 2 == PLAY_ORDER.index(coin) and board[row - 1][column] == EMPTY:
            return score_bonus * (ROW_LEN - row)
    return 0


def available_columns(board):
    options = []
    for (x, top) in enumerate(board[ROW_LEN - 1]):
        if top == EMPTY:
            options.append(x)
    return options


def minimax(board, depth, alpha, beta, maximising_player):
    if depth == 0:
        return None, score_position(board)
    elif len(available_columns(board)) == 0:
        return None, 0
    elif is_game_won(board) == AI:
        return None, HIGH_VALUE
    elif is_game_won(board) == PLAYER:
        return None, -HIGH_VALUE

    best_column = None

    if maximising_player:
        best_score = -math.inf
        for column in available_columns(board):
            next_board = board.copy()
            drop_coin(column, AI, next_board)
            next_score = minimax(next_board, depth - 1, alpha, beta, False)[1]
            if best_score < next_score:
                best_score = next_score
                best_column = column

            alpha = max(best_score, alpha)
            if alpha >= beta:
                break
            if alpha == HIGH_VALUE:
                return best_column, best_score

    else:
        best_score = math.inf
        for column in available_columns(board):
            next_board = board.copy()
            drop_coin(column, PLAYER, next_board)
            next_score = minimax(next_board, depth - 1, alpha, beta, True)[1]
            if best_score > next_score:
                best_score = next_score
                best_column = column

            beta = min(best_score, beta)
            if alpha >= beta:
                break
            if beta == -HIGH_VALUE:
                return best_column, best_score

    if best_column is None:
        best_column = random.choice(available_columns(board))
    return best_column, best_score


# this is what is called by main function
# should return index of column (0 to 6 inclusive)
def ai():
    if np.count_nonzero(BOARD) <= 2:
        return COLUMN_LEN // 2
    results = minimax(BOARD, AI_DEPTH, -math.inf, math.inf, True)
    print(results[1])
    return results[0]


# //-----------------------------------------AI_END-----------------------------------------//


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    turn = PLAY_ORDER[0]

    running = True
    while running:
        draw_board(win)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0]
                draw_mouse(win, mouse_x, turn)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x = event.pos[0]
                column = math.floor(mouse_x / SQUARESIZE)

                if turn == PLAYER:
                    if drop_coin(column, turn, BOARD):
                        turn = AI

                draw_board(win)
                pygame.display.update()

                if not is_game_won(BOARD) == 0:
                    running = False


        if turn == AI and running:
            start = time.time()
            if drop_coin(ai(), turn, BOARD):
                turn = PLAYER
                end = time.time()
                print(end - start)

            if not is_game_won(BOARD) == 0:
                running = False

    print(np.flipud(BOARD))
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
