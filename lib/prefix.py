from discord import Message
from discord.ext.commands import Bot, when_mentioned_or

__all__ = "get_prefix",

async def get_prefix(bot: Bot, message: Message):
    return when_mentioned_or("j.")(bot, message)