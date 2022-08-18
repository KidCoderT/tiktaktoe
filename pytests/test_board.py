from random import randint
import pytest
from src.board import Board
from src.utils import InvalidPositionError


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


def test_board_initial_setup_correct(my_board):
    """1. Test and makes sure that the board state is set correctly"""
    assert my_board.state == Board.GAME_STATE.PLAYING
    assert my_board.turn == "x"
    assert my_board.winner is None
    assert my_board.last_move is None


def test_all_positions_present(my_board, valid_board_positions):
    """2. Test and makes sure that the board positions are present"""
    for (file, rank) in valid_board_positions:
        assert my_board.get_position(file, rank) == " "


def test_incorrect_board_position_raises_error(my_board):
    """3. Make Sure accessing wrong board position raises error"""
    list_of_board_positions = [(randint(-50, -3), randint(30, 50)) for _ in range(50)]

    for position in list_of_board_positions:
        with pytest.raises(InvalidPositionError):
            my_board.get_position(*position)


def test_undo_not_possible_at_start(my_board):
    """4. You cant undo a move at the beginning of the game"""
    with pytest.raises(Exception, match="you cant undo at the beginning of the game"):
        my_board.undo()


@pytest.mark.parametrize("position", [(1, 1), (2, 2), (0, 0), (0, 2), (1, 0), (2, 1)])
def test_play_and_undo_method(my_board, position):
    """5. Test the play and undo methods of the game"""
    my_board.play(*position)
    assert my_board.turn == "o"
    assert my_board.get_position(*position) == "x"
    assert my_board.winner is None

    my_board.undo()
    assert my_board.turn == "x"
    assert my_board.get_position(*position) == " "
    assert my_board.winner is None


@pytest.mark.parametrize("position", [(1, 1), (2, 2), (0, 0), (0, 2), (1, 0), (2, 1)])
def test_last_move_method_works(my_board, position):
    """6. Make Sure the last move method works"""
    assert my_board.last_move is None
    my_board.play(*position)

    assert my_board.last_move == position


def test_play_not_possible_at_end(my_board):
    """7. You cant play a move at the end of the game"""
    my_board.play(0, 0)
    my_board.play(1, 0)
    my_board.play(0, 1)
    my_board.play(1, 1)
    my_board.play(0, 2)

    assert my_board.turn == "o"
    assert my_board.winner == "x"
    assert my_board.state == Board.GAME_STATE.GAME_OVER

    for position in [(0, 0), (0, 1), (0, 2)]:
        assert my_board.get_position(*position) == "x"

    for position in [(1, 0), (1, 1)]:
        assert my_board.get_position(*position) == "o"

    with pytest.raises(Exception):
        my_board.play(1, 2)


def test_reset_board_method(my_board, valid_board_positions):
    """8. Make sure reset_board method works"""

    my_board.play(0, 0)
    my_board.play(1, 0)
    my_board.play(0, 1)
    my_board.play(1, 1)
    my_board.play(0, 2)

    assert my_board.turn == "o"
    assert my_board.winner == "x"
    assert my_board.state == Board.GAME_STATE.GAME_OVER

    my_board.reset_board()

    assert my_board.state == Board.GAME_STATE.PLAYING
    assert my_board.turn == "x"
    assert my_board.winner is None
    assert my_board.last_move is None

    for (file, rank) in valid_board_positions:
        assert my_board.get_position(file, rank) == " "
