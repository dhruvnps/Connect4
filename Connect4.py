import pygame
import numpy as np
import math

ROW_LEN, COLUMN_LEN = 6, 7
BOARD = np.zeros((ROW_LEN, COLUMN_LEN))

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (217, 83, 79)
YELLOW = (220, 150, 60)

SQUARESIZE = 98
RADIUS = int(SQUARESIZE / 3)

WIN_HEIGHT = (ROW_LEN + 1) * SQUARESIZE
WIN_WIDTH = COLUMN_LEN * SQUARESIZE


def drop_coin(column, coin):
    for row in range(ROW_LEN):
        if BOARD[row][column] == 0:
            BOARD[row][column] = coin
            return True
    return False


def draw_board(win):
    win.fill(WHITE)
    pygame.draw.rect(win, BLACK, (0, SQUARESIZE, WIN_WIDTH, WIN_HEIGHT))

    for column in range(COLUMN_LEN):
        for row in range(ROW_LEN):
            color = WHITE
            if BOARD[row][column] == 1:
                color = RED
            elif BOARD[row][column] == 2:
                color = YELLOW
            pygame.draw.circle(win, color, (int((column + 0.5) * SQUARESIZE), int((ROW_LEN - (row - 0.5)) * SQUARESIZE)), RADIUS)


def draw_mouse(win, mouse_x, turn):
    if turn == 1:
        color = RED
    else:
        color = YELLOW
    pygame.draw.circle(win, color, (mouse_x, int(SQUARESIZE / 2)), RADIUS)

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

    running = True
    while running:
        draw_board(win)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0]
                draw_mouse(win, mouse_x, turn)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x = event.pos[0]
                column = int(math.floor(mouse_x / SQUARESIZE))

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
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
