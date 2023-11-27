import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

N = 4
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = N

board = np.zeros((ROW_COUNT,COLUMN_COUNT))

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def checkDiagonally1(board, playerNumber):
	max = 0
	upper_bound = ROW_COUNT - 1 + COLUMN_COUNT - 1 - (N - 1)
	returnMap = {}
	for i in range(1, N + 1):
		returnMap[i] = 0
	for k in range(N - 1, upper_bound + 1):
		max = 0
		if k < COLUMN_COUNT:
			x = k
		else:
			x = COLUMN_COUNT - 1
		y = -x + k
		while x >= 0 and y < ROW_COUNT:
			if board[ROW_COUNT - 1 - y][x] == playerNumber:
				max += 1
				if y == (ROW_COUNT - 1):
					returnMap[max] += 1
			else:
				if max > 0 and max <= N and board[ROW_COUNT - 1 - y][x] == 0:
					returnMap[max] += 1
				max = 0
			x -= 1
			y += 1
	return returnMap

def checkDiagonally2(board, playerNumber):
	max = 0
	upper_bound = COLUMN_COUNT - 1 - (N - 1)
	lower_bound = -(ROW_COUNT - 1 - (N - 1))
	returnMap = {}
	for i in range(1, N + 1):
		returnMap[i] = 0
	for k in range(lower_bound, upper_bound + 1):
		max = 0
		if k >= 0:
			x = k
		else:
			x = 0
		y = x - k
		while x >= 0 and x < COLUMN_COUNT and y < ROW_COUNT:
			if board[ROW_COUNT - 1 - y][x] == playerNumber:
				max += 1
				if y == (ROW_COUNT - 1) or (x == COLUMN_COUNT - 1):
					returnMap[max] += 1
			else:
				if max > 0 and max <= N and board[ROW_COUNT - 1 - y][x] == 0:
					returnMap[max] += 1
				max = 0
			x += 1
			y += 1
	return returnMap

def checkHorizontally(board, playerNumber):
	max = 0
	returnMap = {}
	for i in range(1, N + 1):
		returnMap[i] = 0
	for i in range(ROW_COUNT):
		max = 0
		for j in range(COLUMN_COUNT):
			if board[i][j] == playerNumber:
				max += 1
				if j == COLUMN_COUNT - 1:
					returnMap[max] += 1
			else:
				if max > 0 and max <= N and board[i][j] == 0:
					returnMap[max] += 1
				max = 0
	return returnMap

def checkVertically(board, playerNumber):
	max = 0
	returnMap = {}
	for i in range(1, N + 1):
		returnMap[i] = 0
	for j in range(COLUMN_COUNT):
		max = 0
		for i in range(ROW_COUNT):
			if board[i][j] == playerNumber:
				max += 1
				if i == ROW_COUNT - 1:
					returnMap[max] += 1
			else:
				if max > 0 and max <= N and board[i][j] == 0:
					returnMap[max] += 1
				max = 0
	return returnMap

def getPlays(board, playerNumber):
	returnMap = {}
	player_h = checkHorizontally(board, playerNumber)
	player_v = checkVertically(board, playerNumber)
	player_d1 = checkDiagonally1(board, playerNumber)
	player_d2 = checkDiagonally2(board, playerNumber)
	for i in range(1, N+1):
		returnMap[i] = player_h[i] + player_v[i] + player_d1[i] + player_d2[i]
	return returnMap

def calcHeuristic(board, MyPlayerPiece):
	h = 0
	constant = 100 / N
	all_single_plays = True
	myPlays = getPlays(board, MyPlayerPiece)
	opp_piece = PLAYER_PIECE
	if MyPlayerPiece == PLAYER_PIECE:
		opp_piece = AI_PIECE
	opponentPlays = getPlays(board, opp_piece)

	for a in range(1, N+1):
		if a > 1:
			all_single_plays = not (myPlays[a] > 0 or opponentPlays[a] > 0)
		h += (constant * a) * math.pow(myPlays[a], a) - (constant * a) * math.pow(opponentPlays[a], a)

	if myPlays[N] > 0 or (myPlays[1] > opponentPlays[1] and all_single_plays):
		h = math.inf

	if opponentPlays[N] > 0:
		h = -math.inf

	return h

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-N+1):
		for r in range(ROW_COUNT):
			for i in range(N):
				if board[r][c+i] != piece:
					break
			else:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-N+1):
			for i in range(N):
				if board[r+i][c] != piece:
					break
			else:
				return True

	# Check positively sloped diagonals
	for c in range(COLUMN_COUNT-N+1):
		for r in range(ROW_COUNT-N+1):
			for i in range(N):
				if board[r+i][c+i] != piece:
					break
			else:
				return True

	# Check negatively sloped diagonals
	for c in range(COLUMN_COUNT-N+1):
		for r in range(N-1, ROW_COUNT):
			for i in range(N):
				if board[r-i][c+i] != piece:
					break
			else:
				return True
	
	# No winning move
	return False

def minimax(board, depth, alpha, beta, maximizingPlayer):
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
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, calcHeuristic(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
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
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

print_board(board)
game_over = False

pygame.init()

# Get the screen info
screen_info = pygame.display.Info()
screen_height = screen_info.current_h

SQUARESIZE = screen_height/(ROW_COUNT+3)

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

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
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					print_board(board)
					draw_board(board)


	# Ask for Player 2 Input
	if turn == AI and not game_over:				

		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			#pygame.time.wait(500)
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(3000)
