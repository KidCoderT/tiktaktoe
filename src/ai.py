"""This module contains functions that help run the ai of tik tak toe"""

from math import inf
from .board import Board, GAME_STATE


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

    score = 0

    if board.winner == "x":
        score = 20 - board.depth
    elif board.winner == "o":
        score = -20 + board.depth

    return score


def minimax(
    board: Board, alpha, beta, is_maximizing_player: bool, should_prune: bool
) -> float:
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

    if board.winner is not None or board.state == GAME_STATE.GAME_OVER:
        return score

    if is_maximizing_player:
        best_val = -inf
        for move in board.available_positions():
            board.play(*move)
            evaluation = minimax(board, alpha, beta, False, should_prune)
            board.undo()

            best_val = max(best_val, evaluation)

            if should_prune:
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    return score
        return best_val

    else:
        best_val = inf
        for move in board.available_positions():
            board.play(*move)
            evaluation = minimax(board, alpha, beta, True, should_prune)
            board.undo()

            best_val = min(best_val, evaluation)

            if should_prune:
                beta = min(beta, evaluation)
                if beta <= alpha:
                    return score
        return best_val


def get_best_move(board: Board, is_hard: bool = False) -> tuple:
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
        value = minimax(board, -inf, inf, board.turn == "x", not is_hard) * sign
        is_best_val = value >= best_val

        if is_best_val:
            best_val = value
            best_move = move

        board.undo()

    return best_move
