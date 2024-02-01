from disnake.ext.commands import Cog, Bot, Context, command

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(Template(bot))

class Template(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

