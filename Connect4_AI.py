import pygame
import numpy as np
import math
import random
import time
import signal


AI_TIME = 3

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
# PLAY_ORDER.reverse()
# random.shuffle(PLAY_ORDER)

GRID_SIZE = 98
RADIUS = int(GRID_SIZE / 2.7)
THICKNESS = 7

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
    if np.array_equal(previous_board, current_board):
        return

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

    pygame.draw.circle(win, color, (selected_x, int(GRID_SIZE / 2)), RADIUS)
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
                scan.append([board[row + i][column + i] for i in range(4)])
                # row index for every coin of scan for odd-even strategy
                locations.append([(row + i, column + i) for i in range(4)])

    return scan, locations


# //----------------------------------------AI_START----------------------------------------//


# initialises random table for zobrist hashing
ZOB_TABLE = []
for _ in range(ROW_LEN):
    ZOB_TABLE.append([[random.randint(1, 2**64 - 1) for _ in range(2)] for _ in range(COLUMN_LEN)])

# cache table will contain hashes, calculation depths, and scores of calculated boards
CACHE_TABLE = [[], [], [], []]
CACHE_MAX = 2800


def calculate_hash(board):
    hash = 0
    for row in range(ROW_LEN):
        for column in range(COLUMN_LEN):
            if board[row][column] != EMPTY:
                # coin index must be either 0 or 1
                coin_index = int(board[row][column]) - 1
                # alters hash of board based on coin using zobrist hashing
                hash ^= ZOB_TABLE[row][column][coin_index]
    return hash


def score_position(board):
    score = 0
    scan, locations = scan_fours(board)

    for i in range(len(scan)):
        # score positively for combinations made by AI
        if scan[i].count(AI) == 4:
            score += 100

        elif scan[i].count(AI) == 3 and scan[i].count(EMPTY) == 1:
            score += 5

            # use odd-even strategy for AI
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, AI, empty_location, 100)

        elif scan[i].count(AI) == 2 and scan[i].count(EMPTY) == 2:
            score += 2

        # score negatively for combinations made by PLAYER
        if scan[i].count(PLAYER) == 3 and scan[i].count(EMPTY) == 1:
            score += -4

            # block odd-even strategy from PLAYER
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, PLAYER, empty_location, -100)

    # score positively for AI coins in center column
    center_column = [board[i][COLUMN_LEN // 2] for i in range(ROW_LEN)]
    score += 3 * center_column.count(AI)

    return score


def odd_even_strategy(board, coin, location, score_bonus):
    row, column = location
    if row > 0:
        # rewards applying the odd-even strategy
        # if the even/odd player has a hanging combination on the respective even/odd row
        if row % 2 == PLAY_ORDER.index(coin) and board[row - 1][column] == EMPTY:
            # reward combinations lower down more greatly
            return score_bonus * (ROW_LEN - row)
    return 0


def available_columns(board):
    options = []
    # enumerate over top row of board through all columns
    for (column, column_top) in enumerate(board[ROW_LEN - 1]):
        if column_top == EMPTY:
            options.append(column)

    # sorts the options list by distance to centre column
    # this is so that minimax checks columns in optimal order for alpha beta pruning
    return sorted(options, key=lambda x: abs(x - COLUMN_LEN // 2))


def minimax(board, depth, alpha, beta, maximising_player):
    best_column = None
    hash = calculate_hash(board)

    if depth == 0:
        return None, score_position(board)
    elif is_game_won(board) == AI:
        return None, HIGH_VALUE
    elif is_game_won(board) == PLAYER:
        return None, -HIGH_VALUE
    elif len(available_columns(board)) == 0:
        return None, 0

    # check it cache table can be used for given board
    if hash in CACHE_TABLE[0]:
        hash_index = CACHE_TABLE[0].index(hash)
        calculation_depth = CACHE_TABLE[1][hash_index]
        if calculation_depth >= depth:
            # return the best column and best score based on the previous calculation
            return CACHE_TABLE[2][hash_index], CACHE_TABLE[3][hash_index]

    # returns move that will result in BEST outcome for AI
    if maximising_player:
        best_score = -math.inf
        for column in available_columns(board):
            next_board = board.copy()
            drop_coin(column, AI, next_board)
            next_score = minimax(next_board, depth - 1, alpha, beta, False)[1]
            if best_score < next_score:
                best_score = next_score
                best_column = column

            # alpha beta pruning
            alpha = max(best_score, alpha)
            if alpha >= beta:
                break
            if alpha == HIGH_VALUE:
                return best_column, best_score

    # returns move that will result in WORST outcome for AI
    else:
        best_score = math.inf
        for column in available_columns(board):
            next_board = board.copy()
            drop_coin(column, PLAYER, next_board)
            next_score = minimax(next_board, depth - 1, alpha, beta, True)[1]
            if best_score > next_score:
                best_score = next_score
                best_column = column

            # alpha beta pruning
            beta = min(best_score, beta)
            if alpha >= beta:
                break
            if beta == -HIGH_VALUE:
                return best_column, best_score

    if best_column is None:
        best_column = random.choice(available_columns(board))

    # add results of calculation to cache table
    items_to_add = [hash, depth, best_column, best_score]
    if hash in CACHE_TABLE[0]:
        # remove lower depth calculations of calculated board
        hash_index = CACHE_TABLE[0].index(hash)
        for i in CACHE_TABLE:
            i.pop(hash_index)
    for (x, i) in enumerate(items_to_add):
        CACHE_TABLE[x].append(i)

    # cull cache table
    if len(CACHE_TABLE[0]) > CACHE_MAX:
        for i in range(len(CACHE_TABLE)):
            CACHE_TABLE[i] = CACHE_TABLE[i][-CACHE_MAX:]

    return best_column, best_score


def handler(signum, frame):
    raise Exception


# this is what is called by main function
# should return index of column (0 to 6 inclusive)
def ai():
    # first 2 moves should always be centre column
    if np.count_nonzero(BOARD) <= 2:
        time.sleep(1)
        return COLUMN_LEN // 2

    # never be first to place coin in column other than center
    center_column = [BOARD[row][COLUMN_LEN // 2] for row in range(ROW_LEN)]
    if COLUMN_LEN // 2 in available_columns(BOARD):
        if np.subtract(np.count_nonzero(BOARD), np.count_nonzero(center_column)) == 0:
            time.sleep(1)
            return COLUMN_LEN // 2

    # if no preset move, calculate best move
    start = time.time()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(AI_TIME)

    try:
        # iterative deepening of minimax search
        depth = 1
        results = None
        while True:
            results = minimax(BOARD, depth, -math.inf, math.inf, True)
            depth += 1
            if results[1] == HIGH_VALUE:
                signal.alarm(0)
                time.sleep(1)
                raise Exception

    except Exception:
        print("TIME: " + str(time.time() - start))
        print("DEPTH: " + str(depth))
        print("SCORE: " + str(results[1]))
        return results[0]


# //-----------------------------------------AI_END-----------------------------------------//


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    draw_board(win, BOARD)

    turn = PLAY_ORDER[0]

    running = True
    while running:
        # AI input
        if turn == AI:
            previous_board = BOARD.copy()

            if drop_coin(ai(), turn, BOARD):
                turn = PLAYER

            draw_board(win, BOARD)
            show_newest_coin(win, previous_board, BOARD)
            pygame.display.update()

            if is_game_won(BOARD) != 0 or len(available_columns(BOARD)) == 0:
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

                    if is_game_won(BOARD) != 0 or len(available_columns(BOARD)) == 0:
                        running = False

    print(np.flipud(BOARD))
    pygame.time.wait(10000)


if __name__ == "__main__":
    main()
