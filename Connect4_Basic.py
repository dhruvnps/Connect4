import pygame
import numpy as np
import math

ROW_LEN, COLUMN_LEN = 6, 7
BOARD = np.zeros((ROW_LEN, COLUMN_LEN))

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (217, 60, 79)
YELLOW = (250, 150, 60)

GRID_SIZE = 98
RADIUS = int(GRID_SIZE / 3)

WIN_HEIGHT = (ROW_LEN + 1) * GRID_SIZE
WIN_WIDTH = COLUMN_LEN * GRID_SIZE


def drop_coin(column, coin):
    for row in range(ROW_LEN):
        if BOARD[row][column] == 0:
            BOARD[row][column] = coin
            return True
    return False


def draw_board(win):
    win.fill(WHITE)
    pygame.draw.rect(win, BLACK, (0, GRID_SIZE, WIN_WIDTH, WIN_HEIGHT))

    for column in range(COLUMN_LEN):
        for row in range(ROW_LEN):
            color = WHITE
            if BOARD[row][column] == 1:
                color = RED
            elif BOARD[row][column] == 2:
                color = YELLOW
            pygame.draw.circle(win, color, (int((column + 0.5) * GRID_SIZE), int((ROW_LEN - (row - 0.5)) * GRID_SIZE)), RADIUS)


def draw_mouse(win, mouse_x, turn):
    if turn == 1:
        color = RED
    else:
        color = YELLOW

    column = math.floor(mouse_x / GRID_SIZE)
    pygame.draw.circle(win, color, (int((column + 0.5) * GRID_SIZE), int(GRID_SIZE / 2)), RADIUS)

    pygame.display.update()


def win_check():
    for y in range(ROW_LEN):
        for x in range(COLUMN_LEN):
            row, column, d1, d2 = None, None, None, None

            if x + 3 < COLUMN_LEN:
                row = [BOARD[y][x + i] for i in range(4)]

            if y + 3 < ROW_LEN:
                column = [BOARD[y + i][x] for i in range(4)]

            if y - 3 < ROW_LEN and x + 3 < COLUMN_LEN:
                d1 = [BOARD[y - i][x + i] for i in range(4)]

            if y + 3 < ROW_LEN and x + 3 < COLUMN_LEN:
                d2 = [BOARD[y + i][x + i] for i in range(4)]

            if ([1 for i in range(4)] in (row, column, d1, d2)) or ([2 for i in range(4)] in (row, column, d1, d2)):
                return True
    return False


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    turn = 1
    first_refresh = True

    running = True
    while running:
        draw_board(win)

        if first_refresh:
            first_refresh = False
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0]
                draw_mouse(win, mouse_x, turn)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x = event.pos[0]
                column = int(math.floor(mouse_x / GRID_SIZE))

                if turn == 1:
                    drop_coin(column, turn)
                    turn = 2

                else:
                    drop_coin(column, turn)
                    turn = 1

                draw_board(win)
                draw_mouse(win, mouse_x, turn)
                pygame.display.update()

                if win_check():
                    running = False

    print(np.flipud(BOARD))
    pygame.time.wait(10000)


if __name__ == "__main__":
    main()
