import pygame
import numpy as np
import math
import random
import time

AI_DEPTH = 5

ROW_LEN, COLUMN_LEN = 6, 7
BOARD = np.zeros((ROW_LEN, COLUMN_LEN))

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (217, 60, 79)
YELLOW = (250, 150, 60)
HIGHLIGHT = (255, 255, 255)

EMPTY = 0
PLAYER = 1
AI = 2

PLAY_ORDER = [PLAYER, AI]
# random.shuffle(PLAY_ORDER)

GRID_SIZE = 98
RADIUS = int(GRID_SIZE / 3)
THICKNESS = 5

WIN_HEIGHT = (ROW_LEN + 1) * GRID_SIZE
WIN_WIDTH = COLUMN_LEN * GRID_SIZE

HIGH_VALUE = 1000000


def drop_coin(column, coin, board_input):
    row = next_row(column, board_input)
    if row is not None:
        board_input[row][column] = coin
        return True
    return False


def next_row(column, board_input):
    for row in range(ROW_LEN):
        if board_input[row][column] == EMPTY:
            return row


def get_position(row, column):
    x = int((column + 0.5) * GRID_SIZE)
    y = int((ROW_LEN - (row - 0.5)) * GRID_SIZE)
    return x, y


def draw_board(win, board_input):
    win.fill(WHITE)
    pygame.draw.rect(win, BLACK, (0, GRID_SIZE, WIN_WIDTH, WIN_HEIGHT))

    for column in range(COLUMN_LEN):
        for row in range(ROW_LEN):
            color = WHITE
            if board_input[row][column] == PLAYER:
                color = RED
            elif board_input[row][column] == AI:
                color = YELLOW

            coin_x, coin_y = get_position(row, column)
            pygame.draw.circle(win, color, (coin_x, coin_y), RADIUS)


def show_newest_coin(win, previous_board, current_board):
    board = np.subtract(current_board, previous_board)
    row, column = np.nonzero(board)
    color = HIGHLIGHT

    coin_x, coin_y = get_position(row[0], column[0])
    pygame.draw.circle(win, color, (coin_x, coin_y), RADIUS, THICKNESS)


def draw_mouse(win, mouse_x, turn):
    if turn == PLAYER:
        color = RED
    else:
        color = YELLOW

    selected_column = math.floor(mouse_x / GRID_SIZE)
    selected_row = next_row(selected_column, BOARD)

    if selected_row is not None:
        selected_x, selected_y = get_position(selected_row, selected_column)
    else:
        return selected_column

    # clears previous renders of this function
    for column in range(COLUMN_LEN):
        empty_row = next_row(column, BOARD)
        if empty_row is not None:
            empty_x, empty_y = get_position(empty_row, column)
            pygame.draw.circle(win, WHITE, (empty_x, empty_y), RADIUS)
    pygame.draw.rect(win, WHITE, (0, 0, WIN_WIDTH, GRID_SIZE))

    pygame.draw.circle(win, color, (selected_x, (GRID_SIZE / 2)), RADIUS)
    pygame.draw.circle(win, HIGHLIGHT, (selected_x, selected_y), RADIUS, THICKNESS)

    pygame.display.update()
    return selected_column


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
    draw_board(win, BOARD)

    turn = PLAY_ORDER[0]

    running = True
    while running:
        # AI input
        if turn == AI and running:
            start = time.time()
            previous_board = BOARD.copy()

            if drop_coin(ai(), turn, BOARD):
                turn = PLAYER
                end = time.time()
                print(end - start)

            draw_board(win, BOARD)
            show_newest_coin(win, previous_board, BOARD)
            pygame.display.update()

            if not is_game_won(BOARD) == 0:
                running = False

        # PLAYER input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0]
                draw_mouse(win, mouse_x, turn)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x = event.pos[0]
                column = draw_mouse(win, mouse_x, turn)
                previous_board = BOARD.copy()

                if turn == PLAYER:
                    if drop_coin(column, turn, BOARD):
                        turn = AI

                draw_board(win, BOARD)
                show_newest_coin(win, previous_board, BOARD)
                pygame.display.update()

                if not is_game_won(BOARD) == 0:
                    running = False

    print(np.flipud(BOARD))
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
