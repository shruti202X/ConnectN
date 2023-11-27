import numpy as np
import random
import pygame
import sys
import math

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

N = 4
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = N

board = np.zeros((ROW_COUNT, COLUMN_COUNT))
board_col = [0] * COLUMN_COUNT


def drop_piece(board, board_col, row, col, piece):
    board[row][col] = piece
    board_col[col] += 1


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    return int(board_col[col])


def print_board(board):
    print(np.flip(board, 0))


def checkDiagonally1(board, board_col, playerNumber):
    returnMap = {i: 0 for i in range(1, N + 1)}

    for j in range(COLUMN_COUNT):
        count = 0
        top_row = int(board_col[j]) - 1
        if top_row == ROW_COUNT:
            continue
        for i in range(top_row, -1, -1):
            if j + top_row - i >= COLUMN_COUNT:
                if count > 0:
                    returnMap[count] += 1
                break
            if board[i][j + top_row - i] == playerNumber:
                count += 1
                if count == N or i == 0:
                    returnMap[count] += 1
                    break
            else:
                if count > 0:
                    returnMap[count] += 1
                break

    return returnMap


def checkDiagonally2(board, board_col, playerNumber):
    returnMap = {i: 0 for i in range(1, N + 1)}

    for j in range(COLUMN_COUNT):
        count = 0
        top_row = board_col[j] - 1
        if top_row == ROW_COUNT:
            continue
        for i in range(top_row, -1, -1):
            if j + i - top_row < 0:
                if count > 0:
                    returnMap[count] += 1
                break
            if board[i][j + i - top_row] == playerNumber:
                count += 1
                if count == N or i == 0:
                    returnMap[count] += 1
                    break
            else:
                if count > 0:
                    returnMap[count] += 1
                break

    return returnMap


def checkHorizontally(board, board_col, playerNumber):
    returnMap = {i: 0 for i in range(1, N + 1)}

    for j in range(COLUMN_COUNT):
        count = 0
        top_row = board_col[j]
        if top_row >= ROW_COUNT:
            continue
        for j2 in range(j + 1, COLUMN_COUNT, 1):
            if board[top_row][j2] == playerNumber:
                count += 1
                if count == N or j2 == COLUMN_COUNT - 1:
                    returnMap[count] += 1
                    break
            else:
                if count > 0:
                    returnMap[count] += 1
                break
        count = 0
        for j2 in range(j - 1, -1, -1):
            if board[top_row][j2] == playerNumber:
                count += 1
                if count == N or j2 == 0:
                    returnMap[count] += 1
                    break
            else:
                if count > 0:
                    returnMap[count] += 1
                break

    return returnMap


def checkVertically(board, board_col, playerNumber):
    returnMap = {i: 0 for i in range(1, N + 1)}

    for j in range(COLUMN_COUNT):
        count = 0
        top_row = int(board_col[j]) - 1
        if top_row == ROW_COUNT:
            continue
        for i in range(top_row, -1, -1):
            if board[i][j] >= playerNumber:
                count += 1
                if count == N or i == 0:
                    returnMap[count] += 1
                    break
            else:
                if count > 0:
                    returnMap[count] += 1
                break

    return returnMap


def getPlays(board, board_col, playerNumber):
    returnMap = {}
    player_h = checkHorizontally(board, board_col, playerNumber)
    player_v = checkVertically(board, board_col, playerNumber)
    player_d1 = checkDiagonally1(board, board_col, playerNumber)
    player_d2 = checkDiagonally2(board, board_col, playerNumber)
    for i in range(1, N + 1):
        returnMap[i] = player_h[i] + player_v[i] + player_d1[i] + player_d2[i]
    return returnMap


def calcHeuristic(board, board_col, MyPlayerPiece):
    h = 0
    constant = 100 / N
    all_single_plays = True
    myPlays = getPlays(board, board_col, MyPlayerPiece)
    opp_piece = PLAYER_PIECE
    if MyPlayerPiece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    opponentPlays = getPlays(board, board_col, opp_piece)

    for a in range(1, N + 1):
        if a > 1:
            all_single_plays = not (myPlays[a] > 0 or opponentPlays[a] > 0)
        h += (constant * a) * math.pow(myPlays[a], a) - (constant * a) * math.pow(
            opponentPlays[a], a
        )

    if myPlays[N] > 0 or (myPlays[1] > opponentPlays[1] and all_single_plays):
        h = math.inf

    if opponentPlays[N] > 0:
        h = -math.inf

    return h


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - N + 1):
        for r in range(ROW_COUNT):
            for i in range(N):
                if board[r][c + i] != piece:
                    break
            else:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - N + 1):
            for i in range(N):
                if board[r + i][c] != piece:
                    break
            else:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - N + 1):
        for r in range(ROW_COUNT - N + 1):
            for i in range(N):
                if board[r + i][c + i] != piece:
                    break
            else:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - N + 1):
        for r in range(N - 1, ROW_COUNT):
            for i in range(N):
                if board[r - i][c + i] != piece:
                    break
            else:
                return True

    # No winning move
    return False


def minimax(board, board_col, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    player_wins = winning_move(board, PLAYER_PIECE)
    ai_wins = winning_move(board, AI_PIECE)
    is_terminal = player_wins or ai_wins or len(valid_locations) == 0
    if depth == 0 or is_terminal:
        if is_terminal:
            if ai_wins:
                return (None, math.inf)
            elif player_wins:
                return (None, -math.inf)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, calcHeuristic(board, board_col, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            bcol_copy = board_col.copy()
            drop_piece(b_copy, bcol_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, bcol_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            bcol_copy = board_col.copy()
            drop_piece(b_copy, board_col, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, board_col, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


print_board(board)
game_over = False

pygame.init()

# Get the screen info
screen_info = pygame.display.Info()
screen_height = screen_info.current_h

SQUARESIZE = screen_height / (ROW_COUNT + 3)

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # print(event.pos)
            # Ask for Player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, board_col, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

    # Ask for Player 2 Input
    if turn == AI and not game_over:
        col, minimax_score = minimax(board, board_col, 5, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            # pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, board_col, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
