from discord.ext.commands import Cog, Bot, Context, command

class Template(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

def setup(bot: Bot):
    bot.add_cog(Template(bot))