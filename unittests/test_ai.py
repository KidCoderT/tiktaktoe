import unittest
from random import randint

from src.ai import evaluate_board, get_best_move
from src.board import Board


class AiTestSuite(unittest.TestCase):
    def setUp(self):
        self.board = Board()

        self.valid_board_positions = []

        for file in range(3):
            for row in range(3):
                self.valid_board_positions.append((file, row))

    def tearDown(self):
        del self.board
        del self.valid_board_positions

    # test evaluate_board method
    def test_evaluate_board_method(self):
        """1. Test Evaluate board method works"""
        for _ in range(100):
            self.assertEqual(0, evaluate_board(self.board, randint(0, 500)))

        self.board.play(0, 0)
        self.board.play(1, 0)
        self.board.play(0, 1)
        self.board.play(1, 1)
        self.board.play(0, 2)

        self.assertEqual(16, evaluate_board(self.board, 4))
        self.board.reset_board()

        self.board.play(0, 0)
        self.board.play(1, 0)
        self.board.play(0, 1)
        self.board.play(1, 1)
        self.board.play(2, 2)
        self.board.play(1, 2)

        self.assertEqual(-15, evaluate_board(self.board, 5))
        self.board.reset_board()

    # test get_best_move method
    def test_get_best_move_method(self):
        """2. checks get the best move"""
        self.board.play(0, 0)
        self.board.play(1, 0)
        self.board.play(0, 1)
        self.board.play(1, 1)

        best_move = get_best_move(self.board)
        self.board.play(*best_move)

        self.assertEqual("o", self.board.turn)
        self.assertEqual("x", self.board.winner)
        self.assertEqual(Board.GAME_STATE.GAME_OVER, self.board.state)


if __name__ == "__main__":
    unittest.main()
