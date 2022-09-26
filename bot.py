# pyright: reportGeneralTypeIssues=false, reportOptionalMemberAccess=false, unnecessary-lambda-assignment=false
"""This is my TicTacToe Discord Bot
Implementation. THis mainly takes care of the discord
connection and messaging
"""

import os
import asyncio
from copy import copy
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.board import Board, GAME_STATE
from src.ai import get_best_move
from src.utils import PlayingAfterGameOverError, PositionAlreadyPlayedOnError

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_ID = int(os.getenv("APPLICATION_ID"))  # type: ignore

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="t#",
    description="Tik Tak Toe Bot",
    case_insensitive=True,
    intents=intents,
    owner_id=912949047650824282,
)

BUTTON_GREY = discord.ButtonStyle.gray
BUTTON_BLUE = discord.ButtonStyle.blurple
BUTTON_GREEN = discord.ButtonStyle.green
BUTTON_RED = discord.ButtonStyle.red

EMOJI_DICT = {
    "x": ":regional_indicator_x:",
    "o": ":regional_indicator_o:",
    " ": ":blue_square:",
}

INFO_MSG = """
Hello And Welcome To TicTacToe!
This is a very simple bot created by KidCoderT
that allows people to play tictactoe against an unbeatable ai!

To start any game type **t#tictactoe** after which you can start playing
and the computer will guid u through.

If ever u feel u want to quit just type **t#quit** or react with
the 🚫 sign.

If u feel the view is lagging react with the 🔃 message!!

Thank you!!
"""


def run_asynchronously(func_, *args, **kwargs):
    """Makes any function run asynchronously
    avoiding the RuntimeError that can come
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        loop.create_task(func_(*args, **kwargs))
    else:
        asyncio.run(func_(*args, **kwargs))


class Game:
    """The game class contains all the methods
    and interactions and details for all the game instance
    """

    def __init__(
        self,
        author: discord.Member | discord.User,
        player: str,
        is_hard: bool,
        message: discord.Message,
        view: discord.ui.View,
    ):
        self.message = message
        self.view = view

        self.author = author
        self.board = Board()
        self.player_name = self.author.name
        self.state = "Your Turn"  # Your Turn | Computer is Thinking
        self.player = player  # x or o
        self.is_hard = is_hard

        self.is_computing_next_game = False
        self.channel = self.message.channel

        self.wins = 0
        self.loses = 0
        self.draws = 0

    def reset_values(self):
        self.is_computing_next_game = False
        self.board.reset_board()

        for button in self.view.children:
            button.reset()  # type: ignore

    async def start_computer(self):
        """Plays the computers move"""
        self.is_computing_next_game = True
        self.state = "Computer Thinking..."

        best_move = get_best_move(copy(self.board), self.is_hard)

        if not self.is_hard:
            await asyncio.sleep(1)

        self.board.play(*best_move)

        index = best_move[0] + best_move[1] * 3
        self.view.children[index].style = BUTTON_RED  # type: ignore
        self.view.children[index].disabled = True  # type: ignore

        self.state = "Your Turn"
        self.is_computing_next_game = False
        await self.update(game_finished=(self.board.state == GAME_STATE.GAME_OVER))

    async def update_messages(self):
        """Updates the embed & view to
        show the current message"""
        turn = self.board.turn
        difficulty = "Easy" if not self.is_hard else "Hard"

        if self.board.state == GAME_STATE.GAME_OVER:
            turn = "NA"

            if self.board.winner is None:
                self.state = "Its a Draw!!"
                self.draws += 1
            elif self.board.winner == self.player:
                self.state = "You Won!!"
                self.wins += 1
            else:
                self.state = "Computer Won!!"
                self.loses += 1

            for button in self.view.children:
                button.disabled = True  # type: ignore

        description = "\n".join(
            map(
                lambda x: f"{x[0]}: {x[1]}",
                (
                    ("Player", self.player_name),
                    ("Current Turn", turn),
                    ("State", self.state),
                    ("Difficulty", difficulty),
                    ("\nWins", self.wins),
                    ("Loses", self.loses),
                    ("Draws", self.draws),
                ),
            )
        )

        update = lambda row: map(lambda text: EMOJI_DICT[text], row)
        board_ui = "\n".join(
            [" | ".join(update(row)) for row in self.board.get_board()]
        )
        description = description + "\n\n" + board_ui

        embed = discord.Embed(
            title=":regional_indicator_x: __**TICTACTOE**__ :regional_indicator_o:",
            description=description,
        )

        for rank in range(3):
            for file in range(3):
                index = file + rank * 3
                piece = self.board.get_position(file, rank)

                if piece != " ":
                    if piece != self.player:
                        self.view.children[index].style = BUTTON_RED
                    else:
                        self.view.children[index].style = BUTTON_GREEN

                    self.view.children[index].disabled = True

                else:
                    if self.state == GAME_STATE.GAME_OVER:
                        self.view.children[index].disabled = True

        await self.message.edit(embed=embed, view=self.view)

    async def update(self, move: Optional[tuple] = None, game_finished=False):
        """Updates the Game in the backend"""
        if move is not None:
            if self.is_computing_next_game:
                await self.channel.send(
                    f"{self.author.mention} Wait!! The Computer has not\n"
                    + "yet finished playing his move!!"
                )
            else:
                try:
                    self.board.play(*move)

                    index = move[0] + move[1] * 3
                    self.view.children[index].style = BUTTON_GREEN  # type: ignore
                    self.view.children[index].disabled = True  # type: ignore

                    game_finished = self.board.state == GAME_STATE.GAME_OVER
                except PlayingAfterGameOverError:
                    pass
                except PositionAlreadyPlayedOnError:
                    pass

        if self.board.state != GAME_STATE.GAME_OVER:
            if self.board.turn != self.player:
                self.state = "Computer Thinking..."
                run_asynchronously(self.start_computer)

            if self.board.turn == self.player:
                self.state = "Your Turn"

        await self.update_messages()

        if game_finished:
            should_continue = (
                await get_input(
                    self.channel,
                    "Want to play again??",
                    [("Yes", BUTTON_GREEN, "yes"), ("No", BUTTON_RED, "no")],
                    self.author.id,
                )
                == "yes"
            )

            if should_continue:
                self.reset_values()
                self.player = await get_input(
                    self.channel,
                    "Choose who u are!!",
                    [("X", BUTTON_BLUE, "x"), ("O", BUTTON_GREEN, "o")],
                    self.author.id,
                )

                await self.update()
                return

            await end_game(self.author.id)

    async def quit(self):
        """Quit the game"""
        description = ":red_circle::red_circle: FINISHED :red_circle::red_circle:\n\n"

        difficulty = "Easy" if not self.is_hard else "Hard"
        description = description + "\n".join(
            map(
                lambda x: f"{x[0]}: {x[1]}",
                (
                    ("Player", self.player_name),
                    ("Difficulty", difficulty),
                    ("Wins", self.wins),
                    ("Loses", self.loses),
                    ("Draws", self.draws),
                ),
            )
        )

        embed = discord.Embed(
            title=":regional_indicator_x: __**TICTACTOE**__ :regional_indicator_o:",
            description=description,
        )

        await self.message.edit(embed=embed, view=None)


games: dict[int, Game] = {}


async def end_game(user_id: int):
    """Ends a game based on the player's ID'
    Args: id (int): the id of the player playing the game
    """
    await games[user_id].channel.send(
        f"{bot.get_user(user_id).mention} Thx for Playing!!"
    )
    await games[user_id].quit()
    del games[user_id]


async def get_input(ctx, question, buttons, user_id=None) -> str:
    """This function allows for getting user input
    based on button interactions from the user.

    Args:
        ctx (_type_): the channel to send the question to
        question (_type_): the question to be displayed
        buttons (_type_): the buttons data
        id (_type_, optional): the id if its not accessible through ctx. Defaults to None.

    Returns:
        str: the custom_id of the selected button
    """
    if user_id is None:
        user_id = ctx.author.id

    view = discord.ui.View()

    async def callback(interaction: discord.Interaction):
        await message.delete()

    for (label, style, value) in buttons:
        button = discord.ui.Button(
            label=label, style=style, custom_id=f"{user_id} {value}"
        )
        button.callback = callback

        view.add_item(button)

    message = await ctx.send(f"{bot.get_user(user_id).mention} {question}", view=view)

    def check(interaction: discord.Interaction):
        return (
            interaction.data["component_type"] == 2  # type: ignore
            and "custom_id" in interaction.data.keys()
        )

    res: discord.Interaction = await bot.wait_for(
        "interaction",
        check=check,
    )

    return res.data["custom_id"].split()[-1]  # type: ignore


class PositionalButton(discord.ui.Button):
    """My Custom Discord Button"""

    def __init__(self, user_id: int, file, rank):
        super().__init__(label=" - ", style=BUTTON_GREY, row=rank)
        self.user_id = user_id
        self.file, self.rank = file, rank

    async def callback(self, interaction):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                f"{interaction.user.mention} This is someone elses game u cant interfere!!"
            )
            return

        game = games[self.user_id]
        if self.style == BUTTON_GREY:
            await interaction.response.defer()
            await game.update((self.file, self.rank))

        else:
            await interaction.response.send_message(
                f"{bot.get_user(self.user_id).mention} The position has already been played on!!"
            )

    def reset(self):
        """resets the button
        to original state
        and color!!
        """
        self.disabled = False
        self.style = BUTTON_GREY


# tictactoe
# - starts a new game
# - create the buttons & embed
# - create the game representation
# - adds the game to the list of games


@bot.command()
async def tictactoe(ctx: commands.Context):
    """Starts a new Game With the Bot

    Args:
        ctx (commands.Context): the channel
    """
    author = ctx.author.id

    if author not in games:

        player = await get_input(
            ctx,
            "Choose who u are!!",
            [("X", BUTTON_BLUE, "x"), ("O", BUTTON_GREEN, "o")],
            author,
        )
        is_hard = (
            await get_input(
                ctx,
                "Choose your difficulty level!!",
                [("Easy", BUTTON_GREEN, "easy"), ("Hard", BUTTON_RED, "hard")],
            )
            == "hard"
        )

        description = "loading...."
        embed = discord.Embed(
            title=":regional_indicator_x: __**TICTACTOE**__ :regional_indicator_o:",
            description=description,
        )

        view = discord.ui.View(timeout=None)

        for rank in range(3):
            for file in range(3):
                btn = PositionalButton(author, file, rank)
                view.add_item(btn)

        message = await ctx.send(embed=embed, view=view)
        await message.add_reaction("🚫")
        await message.add_reaction("🔃")

        new_game = Game(
            ctx.author,
            player,
            is_hard,
            message,
            view,
        )
        games[author] = new_game

        await games[author].update()

    else:
        await ctx.send(f"{ctx.author.mention} u are already in a game!!")
        await ctx.send("either quit and restart or continue")


# quit
# - quits the game the player is playing
# - if player not playing game just say problem


@bot.command(name="quit")
async def quit_game(ctx: commands.Context):
    """Quits any and all existing games

    Args:
        ctx (commands.Context): _description_
    """
    author = ctx.author.id

    if author not in games:
        await ctx.send(f"{ctx.author.mention} u are not playing any game!!")
        await ctx.send("start a new game by typing **t#tictactoe**")

    else:
        await end_game(ctx.author.id)


# clear_all <n>
# - deletes all the bot messages in the last n messages
# - only possible if bot maker or server owner


@bot.command()
async def clear_all(ctx: commands.Context, length):
    """Clear All the Messages made by the Bot.

    Args:
        ctx (commands.Context): the COntext
        length (str): the number of messages to clear
    """

    def is_bot_message(message: discord.Message):
        try:
            return message.author.id == BOT_ID or message.content.split("#")[0] == "t"
        except IndexError:
            return False

    if ctx.author == ctx.guild.owner or ctx.author.id == bot.owner_id:
        try:
            await ctx.channel.purge(limit=int(length), check=is_bot_message)  # type: ignore
            await ctx.send(f"{ctx.author.mention} Deleted all previous Messages!!")

            games.clear()
        except ValueError:
            await ctx.send(f"{ctx.author.mention} length needs to be a number!!")

        return

    await ctx.send(
        f"{ctx.author.mention} You dont have the permission to delete the messages!!"
    )


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """This is the method called when the user
    or bot made a reaction to any message

    Args:
        reaction (discord.Reaction): the reaction made
        user (discord.User): the user that made it
    """
    emoji = reaction.emoji

    if user.bot:
        return

    if emoji == "🚫":
        try:
            await end_game(user.id)
        except KeyError:
            pass

    if emoji == "🔃":
        try:
            game = games[user.id]
            await game.update_messages()
        except KeyError:
            pass


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    """This is the method called when the user
    or bot removed a reaction to any message

    Args:
        reaction (discord.Reaction): the reaction made
        user (discord.User): the user that made it
    """
    emoji = reaction.emoji

    if user.bot:
        return

    if emoji == "🔃":
        try:
            game = games[user.id]
            await game.update_messages()
        except KeyError:
            pass


# help
# - gives the instructions to use bot


@bot.command(name="info")
async def _help(ctx: commands.Context):
    """Simple function that when called gives
    the user the instructions to use the bot"""
    await ctx.send(INFO_MSG)


if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)  # type: ignore
