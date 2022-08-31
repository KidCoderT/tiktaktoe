# pyright: reportGeneralTypeIssues=false

import os
import re
from typing import Optional

import discord
import discord.utils
from discord.ext import commands
from dotenv import load_dotenv
from multiprocessing import Process, Manager

from src.board import Board
from src.ai import get_best_move
from src.utils import PositionAlreadyPlayedOnError

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="t#",
    description="Tik Tak Toe Bot",
    case_insensitive=True,
    intents=intents,
    owner_ids=[],
)

emoji = {
    "x": ":regional_indicator_x:",
    "o": ":regional_indicator_o:",
    " ": ":blue_square:",
}

convert_to_emoji = lambda text: emoji[text]
games = {}

INFO_MSG = """
Hello And Welcome To TicTacToe!
This is a very simple bot created by KidCoderT
that allows people to play tictactoe against an unbeatable ai!

To start any game type **t#tictactoe** after which you can start playing
with the computer. The computer itself will then ask for what piece you want to
play as and then the game will begin.

when the computer asks you to play type the message **[x], [y]** and off course
you need to fill in the x and y to your choice of position,
for the x 1 is leftmost and 3 is the rightmost position
and for y 1 is the topmost and 3 is the bottommost position.
Note the space between the comma and y is important will fix that later!

If ever you want to relook at the board  type **t#board** and the bot will
show you the arrangement of the board and the piece you are playing as.

And finally to quit any game just type **t#quit**

Thank you!!
"""


def regex_position(argument: str):
    """Using regex this function finds wheter or
    not a string contains positions to play on.

    if the string doesnt contain it then the function
    return None!

    Args:
        argument (str): the string a user will input

    Returns:
        tuple|None: the position to play on
    """
    try:
        position = re.search(r"[123]+,+?\s+[123]", argument).string
        position.replace(" ", "")
        return tuple(map(int, position.split(",")))
    except AttributeError:
        return None


def render_board(board: Board):
    """Simple method to render any board
    to the discord chat

    Args:
        board (Board): the board to render

    Returns:
        str: the text to send that will display the board
    """
    board_ui = "\n".join(board.get_board(update=lambda row: map(convert_to_emoji, row)))
    return board_ui


def check_gameover_and_winner(game_data):
    """Simple function that checks if the game is over
    and returns it along with the winner (if there is one)

    Args:
        game_data (dict): contains the info about the game

    Returns:
        tuple[bool, str]: bool -> is_gameover, str -> winner
    """
    is_gameover = game_data["board"].state == Board.GAME_STATE.GAME_OVER
    winner = game_data["board"].winner
    if winner is None:
        winner = "draw"

    return (is_gameover, winner)


def play_best_move(board, move):
    """Gets the best move

    Args:
        board (Board): The Board
        move (Manager.dict): the best_move dict
    """
    best_move = get_best_move(board)
    move["x"] = best_move[0]
    move["y"] = best_move[1]


async def make_computer_play(ctx: commands.Context, board: Board):
    """This function makes the computer play its turn

    Args:
        ctx (commands.Context): the context that is being used
        board (Board): the current board to play on
    """

    message = await ctx.send("Computer Thinking...")

    with Manager() as manager:
        best_move = manager.dict({"x": -1, "y": -1})

        process = Process(target=play_best_move, args=[board, best_move])
        process.start()
        process.join()

        board.play(best_move["x"], best_move["y"])

    await message.edit(content="Computer Thinking... Done!")
    await ctx.send(render_board(board))
    await ctx.send(
        f"{ctx.author.mention} the computer played {map(lambda x: x + 1, board.last_move)}!"
    )


async def end_game(ctx: commands.Context, winner: str, user_id: str) -> bool:
    """This is the function that runs when the game is over

    Args:
        ctx (commands.Context): the context as of now
        winner (str): the winner
        user_id (str): the id of the user who's playing

    Returns:
        bool: should end the game or not
    """

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    if winner == "draw":
        await ctx.send("It was a Draw!")
        await ctx.send("Nice!")
    elif winner == games[user_id]["computer"]:
        await ctx.send("The Computer Won!")
        await ctx.send("Good Luck Next Time!")
    else:
        await ctx.send(f"{ctx.author.mention} Won!")
        await ctx.send("Great Going!")

    await ctx.send(f"{ctx.author.mention}, are you going to play again? Y or N")
    msg = await bot.wait_for("message", check=check)

    if msg.content.lower() in ("yes", "y", "true", "t", "1", "enable", "on"):
        computer = None

        while computer is None:
            await ctx.send(f"{ctx.author.mention}, are you X or O?")
            msg = await bot.wait_for("message", check=check)

            if msg.content.lower() == "x":
                computer = "o"
            elif msg.content.lower() == "o":
                computer = "x"
            else:
                await ctx.send("Please select either x or o!")

        games[user_id]["computer"] = computer
        games[user_id]["board"].reset_board()

        if games[user_id]["computer"] == "x":
            await make_computer_play(ctx, games[user_id]["board"])

        return False

    elif msg.content.lower() in ("no", "n", "false", "f", "0", "disable", "off"):
        await ctx.send(f"{ctx.author.mention} Thx for playing!")
        await ctx.send("Bye!")

        games.pop(user_id)
        return True


@bot.command()
async def tictactoe(ctx: commands.Context, player_value: Optional[str]):
    """The actual starting point for the game"""

    def is_a_letter(text) -> bool:
        return len(text) == 1

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    if ctx.author.id in games.keys():
        return await ctx.reply(
            "You're already in a game!!\ntype **t#board** to see the current state of the game!"
        )

    game_data = {"board": Board(), "computer": None}

    await ctx.send(f"{ctx.author.mention} Started a new game with AI!")
    await ctx.send("started game!!")
    await ctx.send(render_board(game_data["board"]))

    if player_value is not None:
        singular_letters = filter(is_a_letter, player_value.split(" "))
        game_data["computer"] = "o" if "x" in singular_letters else "x"

    else:
        while game_data["computer"] is None:
            await ctx.send(f"{ctx.author.mention} Are you X or O?")
            msg = await bot.wait_for("message", check=check)

            if msg.content.lower() not in ["x", "o"]:
                await ctx.send("Please select either x or o!")
                continue

            if msg.content.lower() == "x":
                game_data["computer"] = "o"
            elif msg.content.lower() == "o":
                game_data["computer"] = "x"
            else:
                await ctx.send("Please select either x or o!")

    if game_data["computer"] == "x":
        await make_computer_play(ctx, game_data["board"])

    await ctx.send(f"{ctx.author.mention} Your Turn!")
    games[ctx.author.id] = game_data

    while game_data["board"].state == Board.GAME_STATE.PLAYING:
        msg = await bot.wait_for("message", check=check)
        position = regex_position(msg.content)

        if ctx.author.id not in games.keys():
            return

        if position is not None:
            try:
                games[ctx.author.id]["board"].play(position[0] - 1, position[1] - 1)
            except PositionAlreadyPlayedOnError:
                await ctx.send(
                    "Select another location as that position has already been played on!"
                )
            else:
                await ctx.send(
                    f"{ctx.author.mention} played {position[0]}, {position[1]}!"
                )
                await ctx.send("current board position:")
                await ctx.send(render_board(games[ctx.author.id]["board"]))

                is_gameover, winner = check_gameover_and_winner(games[ctx.author.id])

                if is_gameover:
                    should_end = await end_game(ctx, winner, ctx.author.id)
                    if should_end:
                        return

                await make_computer_play(ctx, games[ctx.author.id]["board"])

                is_gameover, winner = check_gameover_and_winner(games[ctx.author.id])

                if is_gameover:
                    should_end = await end_game(ctx, winner, ctx.author.id)
                    if should_end:
                        return


@bot.command()
async def board(ctx: commands.Context):
    """Draws the current board for the player when needed"""
    if ctx.author.id not in games.keys():
        return await ctx.send(
            "You have not yet started any game!\n Write **t#info** to know how to use this bot"
        )

    await ctx.send(f"{ctx.author.mention} your current board position:")
    await ctx.send(render_board(games[ctx.author.id]["board"]))
    await ctx.send(
        f"You are playing as {('O' if games[ctx.author.id]['computer'] == 'x' else 'X')}"
    )
    await ctx.send(f"Good Luck!")


@bot.command(name="quit")
async def _quit(ctx: commands.Context):
    """Method to quit a game"""
    if ctx.author.id not in games.keys():
        return await ctx.send(
            "You cant quit a game without even starting it!\n Write **t#info** to know how to use this bot"
        )

    await ctx.send("Thx for playing!")
    await ctx.send("Bye!")

    games.pop(ctx.author.id)


@bot.command(name="info")
async def _help(ctx: commands.Context):
    """Simple function that when called gives
    the user the instructions to use the bot"""
    await ctx.send(INFO_MSG)


if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
