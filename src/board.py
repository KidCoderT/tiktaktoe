"""This module contains the board class containing the logic and commands
to use the board
"""

from enum import Enum
from src.utils import *


class Board:
    """This is the game board for tic tak toe"""

    class GAME_STATE(Enum):
        """The Game State of the Board"""

        PLAYING = 1
        GAME_OVER = 0

    def __init__(self):
        self.__board = [[" " for _ in range(3)] for _ in range(3)]
        self.__played_move = []
        self.turn = "x"
        self.depth = 0

        self.state = self.GAME_STATE.PLAYING
        self.winner = None

    def get_position(self, file: int, rank: int):
        """Get a specified position on the board

        Args:
            file (int): the file to get it from
            rank (int): the rank to get it from

        Raises:
            InvalidPositionError: It is raised when the position is invalid

        Returns:
            _type_: object which contains the position info
        """
        try:
            return self.__board[rank][file]
        except IndexError as error:
            raise InvalidPositionError((file, rank)) from error

    def play(self, file: int, rank: int):
        """Plays a move on the board
        and then changes the current_player

        Args:
            file (int): the file to play the move on
            rank (int): the rank to play the move on

        Raises:
            InvalidPositionError: It is raised when the position is invalid
        """
        if self.state == self.GAME_STATE.GAME_OVER:
            raise PlayingAfterGameOverError()

        if self.__board[rank][file] != " ":
            raise PositionAlreadyPlayedOnError((file, rank))
        try:
            self.__board[rank][file] = self.turn
            self.__played_move.append((file, rank))
            self.check_state()
            self.turn = "o" if self.turn == "x" else "x"
            self.depth += 1
        except IndexError as error:
            raise InvalidPositionError((file, rank)) from error

    def undo(self):
        """Undos the last played move and resets the current_player"""
        if len(self.__played_move) == 0:
            raise Exception("you cant undo at the beginning of the game")

        last_move = self.__played_move.pop(-1)
        self.__board[last_move[1]][last_move[0]] = " "
        self.depth -= 1

        self.state = self.GAME_STATE.PLAYING
        self.winner = None
        self.check_state()

        self.turn = "o" if self.turn == "x" else "x"

    @property
    def last_move(self):
        """gets the last move of the board"""
        if len(self.__played_move) == 0:
            return None
        return self.__played_move[-1]

    def available_positions(self) -> list:
        """Returns a list of all available_positions on the board"""
        _available_positions = []

        for file in range(3):
            for rank in range(3):
                if self.get_position(file, rank) == " ":
                    _available_positions.append((file, rank))

        return _available_positions

    def check_state(self):
        """Checks wheter any side has won or its a draw"""

        # check the rows
        for columns in range(3):
            winner_present = (
                self.__board[0][columns]
                == self.__board[1][columns]
                == self.__board[2][columns]
                != " "
            )
            if winner_present:
                self.winner = self.__board[0][columns]
                self.state = self.GAME_STATE.GAME_OVER
                return

        # check the columns
        for columns in range(3):
            winner_present = (
                self.__board[columns][0]
                == self.__board[columns][1]
                == self.__board[columns][2]
                != " "
            )
            if winner_present:
                self.winner = self.__board[columns][0]
                self.state = self.GAME_STATE.GAME_OVER
                return

        # check diagonals
        winner_present = (
            self.__board[0][0] == self.__board[1][1] == self.__board[2][2] != " "
        )
        if winner_present:
            self.winner = self.__board[1][1]
            self.state = self.GAME_STATE.GAME_OVER
            return

        winner_present = (
            self.__board[2][0] == self.__board[1][1] == self.__board[0][2] != " "
        )
        if winner_present:
            self.winner = self.__board[1][1]
            self.state = self.GAME_STATE.GAME_OVER
            return

        if len(self.available_positions()) == 0:
            self.state = self.GAME_STATE.GAME_OVER

    def reset_board(self):
        """Resets the board to its initial state"""
        self.__board = [[" " for _ in range(3)] for _ in range(3)]
        self.__played_move = []
        self.turn = "x"

        self.state = self.GAME_STATE.PLAYING
        self.winner = None

    def get_board(self, update):
        """Gets the board represented in the form of an array where each element
        shows a row on the board
        """

        return ["|".join(update(row)) for row in self.__board]
