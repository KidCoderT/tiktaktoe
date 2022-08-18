import os

import discord
import discord.utils
from discord.ext import commands
from dotenv import load_dotenv

from src.board import Board

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


def render_board(board: Board):
    board_ui = "\n".join(board.get_board(update=lambda row: map(convert_to_emoji, row)))
    return board_ui


class XorO(commands.Converter):
    async def convert(self, ctx, argument):
        singular_letters = filter(self.is_a_letter, argument.split(" "))
        return "x" if "x" in singular_letters else "y"

    @staticmethod
    def is_a_letter(text) -> bool:
        return len(text) == 1


@bot.command(name="tiktaktoe")
async def start(ctx: commands.Context, *, player_value: XorO):
    try:
        if ctx.author.id in games.keys():
            return await ctx.reply(
                "You're already in a game!!\ntype **$board** to see the current state of the game or **$reset** to reset the game!"
            )

        games[ctx.author.id] = {
            "board": Board(),
            "computer": "o" if player_value == "x" else "x",
        }
        await ctx.send(f"{ctx.author} Started a new game with AI!")
        await ctx.send(f"started game!!")
        await ctx.send(render_board((games[ctx.author.id]["board"])))
    except commands.errors.MissingRequiredArgument as error:
        pass


bot.run(TOKEN, reconnect=True)
