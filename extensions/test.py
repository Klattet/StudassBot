from disnake import AppInfo, TeamMember
from disnake.ext.commands import Cog, Bot, Context, command

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(Test(bot))

class Test(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @command()
    async def test(self, ctx: Context) -> None:
        app_info: AppInfo = await self.bot.application_info()
        team_members: list[TeamMember] = app_info.team.members

        await ctx.reply(f"Team members: {", ".join(member.name for member in team_members)}")
