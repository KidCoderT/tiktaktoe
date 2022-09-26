from src.board import Board
from src.ai import get_best_move
import asyncio
import time


def run_asynchronously(func_, *args, **kwargs):
    """Makes any function run asynchronously
    avoiding the RuntimeError that can come
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        print("loop created")
        task = loop.create_task(func_(*args, **kwargs))
        loop.run_until_complete(task)
    else:
        asyncio.run(func_(*args, **kwargs))


def time_(function_, *args, **kwargs):
    start_time = time.time()
    print(function_(*args, **kwargs))
    print(time.time() - start_time)


def run():
    board = Board()

    return run_asynchronously(
        get_best_move,
        board,
        True,
    )


print(time_(run))
