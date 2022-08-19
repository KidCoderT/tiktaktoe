# pyright: reportGeneralTypeIssues=false

import os
import re
from typing import Optional

import discord
import discord.utils
from discord.ext import commands
from dotenv import load_dotenv

from src.board import Board
from src.ai import get_best_move
from src.utils import PositionAlreadyPlayedOnError

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="#",
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


def regex_position(argument: str):
    try:
        position = re.search(r"[123]+,+?\s+[123]", argument).string
        position.replace(" ", "")
        return tuple(map(int, position.split(",")))
    except AttributeError:
        return None


def render_board(board: Board):
    board_ui = "\n".join(board.get_board(update=lambda row: map(convert_to_emoji, row)))
    return board_ui


def check_gameover_and_winner(game_data) -> tuple[bool, str]:
    is_gameover = game_data["board"].state == Board.GAME_STATE.GAME_OVER
    winner = game_data["board"].winner
    if winner is None:
        winner = "draw"

    return (is_gameover, winner)


async def make_computer_play(ctx: commands.Context, board: Board):
    message = await ctx.send("Computer Thinking...")

    best_move = get_best_move(board)
    board.play(*best_move)

    await message.edit(content="Computer Thinking... Done!")
    await ctx.send(render_board(board))


async def end_game(ctx: commands.Context, winner: str, user_id: str) -> bool:
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    if winner == "draw":
        await ctx.send("It was a Draw!")
        await ctx.send("Nice!")
    elif winner == games[user_id]["computer"]:
        await ctx.send("The Computer Won!")
        await ctx.send("Good Luck Next Time!")
    else:
        await ctx.send("You Won!")
        await ctx.send("Great Going!")

    await ctx.send("Are you going to play again? Y or N")
    msg = await bot.wait_for("message", check=check)

    if msg.content.lower() in ("yes", "y", "true", "t", "1", "enable", "on"):
        computer = None

        while computer is None:
            await ctx.send("Are you X or O?")
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
        await ctx.send("Thx for playing!")
        await ctx.send("Bye!")

        games.pop(user_id)
        return True


@bot.command()
async def tiktaktoe(ctx: commands.Context, player_value: Optional[str]):
    def is_a_letter(text) -> bool:
        return len(text) == 1

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    if ctx.author.id in games.keys():
        return await ctx.reply(
            "You're already in a game!!\ntype **#board** to see the current state of the game or **#reset** to reset the game!"
        )

    game_data = {"board": Board(), "computer": None}

    await ctx.send(f"{ctx.author} Started a new game with AI!")
    await ctx.send("started game!!")
    await ctx.send(render_board(game_data["board"]))

    if player_value is not None:
        singular_letters = filter(is_a_letter, player_value.split(" "))
        game_data["computer"] = "o" if "x" in singular_letters else "x"

    else:
        while game_data["computer"] is None:
            await ctx.send("Are you X or O?")
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

    await ctx.send("Your Turn!")
    games[ctx.author.id] = game_data

    while game_data["board"].state == Board.GAME_STATE.PLAYING:
        msg = await bot.wait_for("message", check=check)
        position = regex_position(msg.content)

        if position is not None:
            try:
                games[ctx.author.id]["board"].play(position[0] - 1, position[1] - 1)
            except PositionAlreadyPlayedOnError:
                await ctx.send(
                    "Select another location as that position has already been played on!"
                )
            else:
                await ctx.send(f"You played {position[0]}, {position[1]}!")

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


@bot.command(name="quit")
async def _quit(ctx: commands.Context):
    if ctx.author.id not in games.keys():
        return await ctx.send(
            "You cant quit a game without even starting it!\n Write **#help** to know how to use this bot"
        )

    await ctx.send("Thx for playing!")
    await ctx.send("Bye!")

    games.pop(ctx.author.id)


bot.run(TOKEN, reconnect=True)
