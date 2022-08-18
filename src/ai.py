"""This module contains functions that help run the ai of tik tak toe"""

from .board import Board


def evaluate_board(board: Board, depth: int) -> int:
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
        return 20 - depth
    elif board.winner == "o":
        return -20 + depth
    else:
        return 0


def minimax(board: Board, depth: int, is_maximizing_player: bool) -> int:
    """This is the minimax function that recursively plays
    and evaluates board posiitons to find the best position.
    it then return te score for the best position.

    Args:
        board (Board): the board to be minimized
        depth (int): the current depth of the function
        is_maximizing_player (bool): checks wheter to minimize or maximize the player

    Returns:
        int: the final score for the position
    """
    score = evaluate_board(board, depth)

    if board.winner is not None or board.state == Board.GAME_STATE.GAME_OVER:
        return score

    if is_maximizing_player:
        best_val = -10000
        for move in board.available_positions():
            board.play(*move)
            best_val = max(best_val, minimax(board, depth + 1, False))
            board.undo()
        return best_val

    else:
        best_val = 100000
        for move in board.available_positions():
            board.play(*move)
            best_val = min(best_val, minimax(board, depth + 1, True))
            board.undo()
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
        value = minimax(board, 0, board.turn == "x") * sign
        is_best_val = value >= best_val

        if is_best_val:
            best_val = value
            best_move = move

        board.undo()

    return best_move
