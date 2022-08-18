import pytest
from random import randint
from src.ai import evaluate_board, get_best_move
from src.board import Board


@pytest.fixture()
def my_board():
    board = Board()

    yield board
    del board


@pytest.fixture(scope="module")
def valid_board_positions(request):
    positions = []

    for file in range(3):
        for row in range(3):
            positions.append((file, row))

    def delete_dict(obj):
        del obj

    request.addfinalizer(lambda: delete_dict(positions))
    return positions


def test_evaluate_board_method(my_board):
    """1. Test Evaluate board method works"""
    for _ in range(100):
        assert evaluate_board(my_board, randint(0, 500)) == 0

    my_board.play(0, 0)
    my_board.play(1, 0)
    my_board.play(0, 1)
    my_board.play(1, 1)
    my_board.play(0, 2)

    assert evaluate_board(my_board, 4) == 16
    my_board.reset_board()

    my_board.play(0, 0)
    my_board.play(1, 0)
    my_board.play(0, 1)
    my_board.play(1, 1)
    my_board.play(2, 2)
    my_board.play(1, 2)

    assert evaluate_board(my_board, 5) == -15
    my_board.reset_board()


def test_get_best_move_method(my_board):
    """2. checks get the best move"""
    my_board.play(0, 0)
    my_board.play(1, 0)
    my_board.play(0, 1)
    my_board.play(1, 1)

    best_move = get_best_move(my_board)
    my_board.play(*best_move)

    assert my_board.turn == "o"
    assert my_board.winner == "x"
    assert my_board.state == Board.GAME_STATE.GAME_OVER
