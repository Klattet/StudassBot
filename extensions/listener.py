from disnake import Message
from disnake.ext.commands import Cog, Bot, Context, command, dm_only

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(Listener(bot))

class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @Cog.listener("on_message")
    @dm_only()
    async def listener(self, message: Message) -> None:
        ...