"""Contains utility methods for the game"""


class InvalidPositionError(IndexError):
    """Custom Exception for invalid position accessing from the code.
    This extends from index error"""

    def __init__(self, position: tuple):
        super().__init__(f"The Code tried to access {position} position on the board!")


class PlayingAfterGameOverError(Exception):
    """Custom Exception for when the player tries a move after
    the game is over"""

    def __init__(self):
        super().__init__(
            "The game is over you cant do anything now until you reset the board!"
        )
