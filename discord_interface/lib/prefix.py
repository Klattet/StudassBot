from typing import Callable, Coroutine

from disnake import Message
from disnake.ext.commands import Bot, when_mentioned_or

__all__ = "get_prefix",

def get_prefix(default_prefix: str) -> Callable[[Bot, Message], Coroutine[None, None, list[str]]]:
    async def closure(bot: Bot, message: Message) -> list[str]:
        return when_mentioned_or(default_prefix)(bot, message)

    return closure
