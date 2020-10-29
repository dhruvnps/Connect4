import random
import math
import pygame
import numpy as np
import time
import signal
import pickle
import os


# maximum seconds AI can take
AI_TIME = 3
AI_VS_AI = False
START = None

ROW_LEN, COLUMN_LEN = 6, 7
BOARD = np.zeros((ROW_LEN, COLUMN_LEN))

BLACK = (30, 30, 30)
WHITE = (200, 200, 200)
RED = (217, 60, 79)
YELLOW = (250, 150, 60)
HIGHLIGHT = (255, 255, 255)

# NOTE: DO NOT CHANGE
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


def draw_mouse(win, mouse_x):
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

    pygame.draw.circle(win, RED, (selected_x, int(GRID_SIZE / 2)), RADIUS)
    pygame.draw.circle(win, HIGHLIGHT, (selected_x, selected_y), RADIUS,
                       THICKNESS)

    pygame.display.update()
    return selected_column


def draw_victory(coin, startpoint, endpoint, win):
    if coin == PLAYER:
        color = RED
    else:
        color = YELLOW
    pygame.time.wait(1000)
    pygame.draw.line(win, color, get_position(*startpoint),
                     get_position(*endpoint), THICKNESS)
    pygame.display.update()


def is_victory(board, win):
    scan, locations = scan_fours(board)

    # if called by main funtion victory must be shown
    if win is not None:
        index = None
        if [PLAYER for _ in range(4)] in scan:
            index = scan.index([PLAYER for _ in range(4)])
            draw_victory(PLAYER, locations[index][0], locations[index][3], win)
        elif [AI for _ in range(4)] in scan:
            index = scan.index([AI for _ in range(4)])
            draw_victory(AI, locations[index][0], locations[index][3], win)

    if [PLAYER for _ in range(4)] in scan:
        return PLAYER
    elif [AI for _ in range(4)] in scan:
        return AI


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
                # row index for every coin of scan for odd-even strategy
                locations.append([(row + i, column) for i in range(4)])

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


# initialises zob table and cache table files
if (not (os.path.exists('cachetable.pickle') and os.path.exists('zobtable.pickle'))):
    import Cache_Init

# loads zob table and cache table files
with open('cachetable.pickle', 'rb') as f:
    CACHE_TABLE = pickle.load(f)
with open('zobtable.pickle', 'rb') as f:
    ZOB_TABLE = pickle.load(f)


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
        if scan[i].count(AI) == 3 and scan[i].count(EMPTY) == 1:
            score += 5

            # use odd-even strategy for AI
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, AI, empty_location, 500)

        elif scan[i].count(AI) == 2 and scan[i].count(EMPTY) == 2:
            score += 2

        # score negatively for combinations made by PLAYER
        if scan[i].count(PLAYER) == 3 and scan[i].count(EMPTY) == 1:
            score += -5

            # block odd-even strategy from PLAYER
            empty_location = list(locations[i])[scan[i].index(EMPTY)]
            score += odd_even_strategy(board, PLAYER, empty_location, -500)

        elif scan[i].count(PLAYER) == 2 and scan[i].count(EMPTY) == 2:
            score += -2

    # score positively/negatively for AI/PLAYER coins respectively in center column
    center_column = [board[i][COLUMN_LEN // 2] for i in range(ROW_LEN)]
    score += 2 * center_column.count(AI)

    return score


def odd_even_strategy(board, coin, location, score_bonus):
    row, column = location

    '''
    # rewards imminent victory in preference of odd-even strategy
    # checks if the turn of the coin in question
    if (np.count_nonzero(board != EMPTY) - PLAY_ORDER.index(coin)) % 2 == 0:
        if row == 0 or board[row - 1][column] != EMPTY:
            # return negative/positive value if bonus is -100/100 respectively
            return (score_bonus / abs(score_bonus)) * (HIGH_VALUE / 10)
    '''

    if row > 0:
        # rewards applying the odd-even strategy
        # if the even/odd player has a hanging combination on the respective even/odd row
        if row % 2 == PLAY_ORDER.index(coin) and board[row - 1][column] == EMPTY:
            # reward combinations lower down more greatly
            return score_bonus * (ROW_LEN - row)

    # if no reward is to be given
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
    # if the time has run out
    if time.time() - START > AI_TIME:
        raise Exception

    best_column = None
    hash = calculate_hash(board)

    if depth == 0:
        return None, score_position(board)
    elif is_victory(board, None) == AI:
        return None, HIGH_VALUE
    elif is_victory(board, None) == PLAYER:
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

    return best_column, best_score


# this is what is called by main function
# should return index of column (0 to 6 inclusive)
def ai(turn):
    board = BOARD.copy()
    if AI_VS_AI:
        # invert 1 and 2 if turn is PLAYER played by ai
        if turn == PLAYER:
            board[board == AI] = -1
            board[board == PLAYER] = AI
            board[board == -1] = PLAYER

    # first 2 moves should always be centre column
    if np.count_nonzero(board) <= 2:
        pygame.time.wait(0 if AI_VS_AI else 500)
        return COLUMN_LEN // 2

    '''
    # never be first to place coin in column other than center
    center_column = [BOARD[row][COLUMN_LEN // 2] for row in range(ROW_LEN)]
    if COLUMN_LEN // 2 in available_columns(BOARD):
        if np.subtract(np.count_nonzero(BOARD), np.count_nonzero(center_column)) == 0:
            pygame.time.wait(0 if AI_VS_AI else 500)
            return COLUMN_LEN // 2
    '''

    # if no preset move, calculate best move
    # set start time
    global START
    START = time.time()

    try:
        # iterative deepening of minimax search
        depth = 1
        results = None
        while True:
            results = minimax(board, depth, -math.inf, math.inf, True)
            depth += 1
            if results[1] == HIGH_VALUE:
                pygame.time.wait(0 if AI_VS_AI else 500)
                raise Exception

    except Exception:
        if AI_VS_AI:
            print("TURN:  " + str(turn))
        print("TIME:  " + str("{0:.2f}".format(time.time() - START)))
        print("DEPTH: " + str(depth))
        print("SCORE: " + "%+d" % (results[1]))
        print(np.flipud(BOARD))
        with open('cachetable.pickle', 'wb') as f:
            pickle.dump(CACHE_TABLE, f)
        return results[0]


# //-----------------------------------------AI_END-----------------------------------------//


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    draw_board(win, BOARD)

    turn = PLAY_ORDER[0]

    running = True
    while running:
        # AI input
        if turn == AI or AI_VS_AI:
            previous_board = BOARD.copy()

            if drop_coin(ai(turn), turn, BOARD):
                turn = PLAYER if turn == AI else AI

            draw_board(win, BOARD)
            show_newest_coin(win, previous_board, BOARD)
            pygame.display.update()

            if is_victory(BOARD, win) is not None or len(available_columns(BOARD)) == 0:
                running = False

        # PLAYER input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if not AI_VS_AI:
                if event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]
                    draw_mouse(win, mouse_x)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x = event.pos[0]
                    column = draw_mouse(win, mouse_x)
                    previous_board = BOARD.copy()

                    if turn == PLAYER:
                        if drop_coin(column, turn, BOARD):
                            turn = AI

                        draw_board(win, BOARD)
                        show_newest_coin(win, previous_board, BOARD)
                        pygame.display.update()

                        if (
                            is_victory(BOARD, win) is not None
                            or len(available_columns(BOARD)) == 0
                        ):
                            running = False

    print("\nFINAL BOARD:")
    print(np.flipud(BOARD))
    if AI_VS_AI:
        pygame.time.wait(500)
    else:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()


if __name__ == "__main__":
    main()
    if AI_VS_AI:
        while True:
            BOARD = np.zeros((ROW_LEN, COLUMN_LEN))
            main()
