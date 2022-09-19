"""This module contains functions that help run the ai of tik tak toe"""

from math import inf
from .board import Board


def evaluate_board(board: Board) -> int:
    """Evaluate the state of the board. THe larger the evaluation
    the better the position

    Args:
        board (Board): the board to evaluate
        depth (int): the depth of the game
        is_x (bool): if the current player is x

    Returns:
        int: the evaluation for the board
    """

    board.check_state()

    if board.winner == "x":
        return 20 - board.depth
    elif board.winner == "o":
        return -20 + board.depth
    else:
        return 0


def minimax(board: Board, alpha, beta, is_maximizing_player: bool) -> float:
    """This is the minimax function that recursively plays
    and evaluates board posiitons to find the best position.
    it then return te score for the best position.

    Args:
        board (Board): the board to be minimized
        is_maximizing_player (bool): checks whether to minimize or maximize the player

    Returns:
        int: the final score for the position
    """
    score = evaluate_board(board)

    if board.winner is not None or board.state == Board.GAME_STATE.GAME_OVER:
        return score

    if is_maximizing_player:
        best_val = -inf
        for move in board.available_positions():
            board.play(*move)
            evaluation = minimax(board, alpha, beta, False)
            best_val = max(best_val, evaluation)
            alpha= max(alpha, evaluation)

            board.undo()

            if beta <= alpha:
                return score
        return best_val

    else:
        best_val = inf
        for move in board.available_positions():
            board.play(*move)
            evaluation = minimax(board, alpha, beta, True)
            best_val = min(best_val, evaluation)
            beta= min(beta, evaluation)

            board.undo()

            if beta <= alpha:
                return score
        return best_val


def get_best_move(board: Board) -> tuple:
    """Gets the best move for a given board

    Args:
        board (Board): the board to check

    Returns:
        tuple: the positions of the best move
    """
    best_val = -1000
    best_move = (-1, -1)
    sign = 1 if board.turn == "x" else -1

    for move in board.available_positions():
        board.play(*move)
        value = minimax(board, -inf, inf, board.turn == "x") * sign
        is_best_val = value >= best_val

        if is_best_val:
            best_val = value
            best_move = move

        board.undo()

    return best_move
