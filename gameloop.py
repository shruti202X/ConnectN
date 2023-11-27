import time
import random
from gamerules import check_end_conditions 
import numpy as np
from helpers import is_board_full,print_board

class Timer:
    def __init__(self):
        self.elapsed = 0
        self.running = True
        self._start = 0
    
    def resume(self):
        self.running = True
        self._start = time.perf_counter()

    def pause(self):
        self.running = False
        self.elapsed += time.perf_counter() - self._start

    def get_elapsed(self):
        return self.elapsed + (time.perf_counter() - self._start if self.running else 0)
    

def create_board(width, height):
    return np.zeros((height, width), dtype=int)

NUM_GAMES = 10
TIME_LIMIT = 60 
a_wins, draws, b_wins = 0, 0, 0
time_A = Timer()
time_B = Timer()

for game_i in range(NUM_GAMES):
    width = random.randint(5,15)
    height = random.randint(width,15)
    n = random.randint(4,width)
    print(f"GAME NUMBER : {game_i}")
    print(f"BOARD : {width} X {height}")
    print(f"Player needs to match {n} tokens to win")
    board = create_board(width, height)
    game_over = False
    whose_turn = 1

    while not game_over:
        if whose_turn == 1:
            from team_A import A_play
            time_A.resume()
            A_play(board,n)
            time_A.pause()
            whose_turn = 0
            if check_end_conditions(board, 1, n):
                print("Player 1 wins!")
                game_over = True
                print_board(board)
                a_wins = a_wins+1

            elif is_board_full(board):
                print("It's a draw!")
                print_board(board)
                game_over = True
                draws = draws+1
            
        else:
            from team_B import B_play
            time_A.resume()
            B_play(board,n)
            time_A.pause()
            whose_turn = 1
            if check_end_conditions(board, 2, n):
                print("Player 2 wins!")
                game_over = True
                print_board(board)
                b_wins = b_wins+1

            elif is_board_full(board):
                print("It's a draw!")
                print_board(board)
                game_over = True
                draws = draws+1
            
print(f"A : {a_wins},DRAWS : {draws} ,B : {b_wins}")

    


       

