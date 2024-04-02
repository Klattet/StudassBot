from disnake import Message
from disnake.ext.commands import Cog, Bot, Context

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(Listener(bot))

class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @Cog.listener("on_message")
    async def listener(self, message: Message) -> None:

        # Filter messages to only relevant ones.
        if message.author.bot or message.guild or (await self.bot.get_context(message)).command: return

        json_package = {
            "id": message.author.id,
            "text:": message.content
        }

        # TODO: Send json package to the server with LLM.