import unittest
from src.board import Board
from src.utils import InvalidPositionError
from random import randint


class BoardTestSuite(unittest.TestCase):
    def setUp(self):
        self.board = Board()

        self.valid_board_positions = []

        for file in range(3):
            for row in range(3):
                self.valid_board_positions.append((file, row))

    def tearDown(self):
        del self.board
        del self.valid_board_positions

    def test_board_setup_correct(self):
        """1. Test and makes sure that the board state is set correctly"""
        self.assertEqual(Board.GAME_STATE.PLAYING, self.board.state)
        self.assertEqual("x", self.board.turn)
        self.assertEqual(None, self.board.winner)
        self.assertEqual(None, self.board.last_move)

    def test_all_positions_present(self):
        """2. Test and makes sure that the board positions are present"""
        for (file, rank) in self.valid_board_positions:
            self.assertEqual(" ", self.board.get_position(file, rank))

    def test_incorrect_board_position_raises_error(self):
        """3. Make Sure accessing wrong board position raises error"""
        list_of_board_positions = [
            (randint(-50, -3), randint(30, 50)) for _ in range(50)
        ]

        for position in list_of_board_positions:
            self.assertRaises(
                InvalidPositionError, self.board.get_position, position[0], position[1]
            )

    def test_undo_not_possible_at_start(self):
        """4. You cant undo a move at the beginning of the game"""
        self.assertRaises(Exception, self.board.undo)

    def test_play_method_and_unplay(self):
        """5. Test the play and undo methods of the game"""
        self.board.play(1, 1)
        self.assertEqual("o", self.board.turn)
        self.assertEqual("x", self.board.get_position(1, 1))
        self.assertEqual(None, self.board.winner)

        self.board.undo()
        self.assertEqual("x", self.board.turn)
        self.assertEqual(" ", self.board.get_position(1, 1))
        self.assertEqual(None, self.board.winner)

    def test_last_move_method_works(self):
        """6. Make Sure the last move method works"""
        self.assertEqual(None, self.board.last_move)
        self.board.play(1, 1)
        self.assertEqual((1, 1), self.board.last_move)

    def test_play_not_possible_at_end(self):
        """7. You cant play a move at the end of the game"""
        self.board.play(0, 0)
        self.board.play(1, 0)
        self.board.play(0, 1)
        self.board.play(1, 1)
        self.board.play(0, 2)

        self.assertEqual("o", self.board.turn)
        self.assertEqual("x", self.board.winner)
        self.assertEqual(Board.GAME_STATE.GAME_OVER, self.board.state)

        for position in [(0, 0), (0, 1), (0, 2)]:
            self.assertEqual("x", self.board.get_position(*position))

        for position in [(1, 0), (1, 1)]:
            self.assertEqual("o", self.board.get_position(*position))

        self.assertRaises(Exception, self.board.play, 1, 2)

    def test_reset_board_method(self):
        """8. Make sure reset_board method works"""

        self.board.play(0, 0)
        self.board.play(1, 0)
        self.board.play(0, 1)
        self.board.play(1, 1)
        self.board.play(0, 2)

        self.assertEqual("o", self.board.turn)
        self.assertEqual("x", self.board.winner)
        self.assertEqual(Board.GAME_STATE.GAME_OVER, self.board.state)

        self.board.reset_board()

        self.assertEqual(Board.GAME_STATE.PLAYING, self.board.state)
        self.assertEqual("x", self.board.turn)
        self.assertEqual(None, self.board.winner)
        self.assertEqual(None, self.board.last_move)

        for (file, rank) in self.valid_board_positions:
            self.assertEqual(" ", self.board.get_position(file, rank))


if __name__ == "__main__":
    unittest.main()
