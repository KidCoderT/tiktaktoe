from copy import deepcopy
from .board import Board


def evaluate_board(board: Board, depth, is_x):
    x_mul = 1 if is_x else -1
    o_mul = -1 if is_x else 1

    if board.winner == "x":
        return (20 * x_mul) - depth
    elif board.winner == "o":
        return (-20 * o_mul) + depth
    else:
        return 0


def minimax(board: Board, depth, isMaximizingPlayer):
    score = evaluate_board(board, depth, isMaximizingPlayer)

    if board.winner != " ":
        return score

    if isMaximizingPlayer:
        bestVal = -10000
        for move in board.available_positions():
            board.play(*move)
            bestVal = max(bestVal, minimax(board, depth + 1, False))
            board.undo()
        return bestVal

    else:
        bestVal = 100000
        for move in board.available_positions():
            board.play(*move)
            bestVal = min(bestVal, minimax(board, depth + 1, True))
            board.undo()
        return bestVal


def get_best_move(board: Board):
    best_val = -1000 if board.turn == "x" else 1000
    best_move = (-1, -1)

    for move in board.available_positions():
        board.play(*move)
        value = minimax(board, 0, board.turn == "x")
        is_best_val = best_val <= value if board.turn == "x" else best_val >= value

        if is_best_val:
            best_val = best_val
            best_move = move

        board.undo()

    return best_move
