import copy

def check_end_conditions(board, player, n):

    for row in range(len(board)):
        for col in range(len(board[0]) - n + 1):
            if all(board[row][col + i] == player for i in range(n)):
                return True
            
    for col in range(len(board[0])):
        for row in range(len(board) - n + 1):
            if all(board[row + i][col] == player for i in range(n)):
                return True

    for row in range(len(board) - n + 1):
        for col in range(len(board[0]) - n + 1):
            if all(board[row + i][col + i] == player for i in range(n)):
                return True

    for row in range(n - 1, len(board)):
        for col in range(len(board[0]) - n + 1):
            if all(board[row - i][col + i] == player for i in range(n)):
                return True

    return False

def generate_future_states(board, player, n):
    future_states = []
    for col in range(len(board[0])):
        if is_valid_move(board, col):
            new_board = copy.deepcopy(board)
            for row in range(n - 1, -1, -1):
                if new_board[row][col] is None:
                    new_board[row][col] = player
                    break
            future_states.append(new_board)
    return future_states

def is_valid_move(board, col):
    return board[0][col] == 0