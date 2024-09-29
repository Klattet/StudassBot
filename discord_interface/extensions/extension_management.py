import os, sys

from disnake import Message, AppInfo
from disnake.ext.commands import Cog, Bot, Context, group, ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed, check

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(ExtensionManagement(bot))

class ExtensionManagement(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @staticmethod
    async def is_team_member(ctx: Context) -> bool:
        """
        Check if the user calling the command is a dev team member.
        """

        app_info: AppInfo = await ctx.bot.application_info()
        is_member: bool = ctx.author in app_info.team.members

        if not is_member:
            await ctx.reply("Only dev team members can use this command.")

        return is_member

    async def load_extension(self, extension_name: str, reply_message: Message) -> None:
        message_content: str = reply_message.content

        print(f"Loading extension: {extension_name}")
        await reply_message.edit(f"{message_content}\nLoading: {extension_name}")

        try:
            self.bot.load_extension(f"extensions.{extension_name}")
            print(f"Loaded extension: {extension_name}")
            await reply_message.edit(f"{message_content}\nLoaded: {extension_name}")
        except ExtensionAlreadyLoaded:
            print(f"Failed to load extension. Extension already loaded: {extension_name}")
            await reply_message.edit(f"{message_content}\nAlready loaded: {extension_name}")
        except ExtensionNotFound:
            print(f"Failed to load extension. Name not found: {extension_name}")
            await reply_message.edit(f"{message_content}\nNo such extension: {extension_name}")
        except (NoEntryPointError, ExtensionFailed) as exception:
            print(f"Failed to load extension. Code failed to execute: {extension_name}")
            print(exception, file = sys.stderr, flush = True)
            await reply_message.edit(f"{message_content}\nCode error: {extension_name}")

    @group(name = "load", invoke_without_command = True)
    @check(is_team_member)
    async def load(self, ctx: Context, *extension_names: str) -> None:
        reply_message: Message = await ctx.reply(f"**Loading {len(extension_names)} extensions:**\n")

        for name in extension_names:
            reply_message = await self.load_extension(name, reply_message)

    @load.command(name = "all")
    @check(is_team_member)
    async def load_all(self, ctx: Context) -> None:
        reply_message: Message = await ctx.reply(f"**Loading all extensions:**\n")

        for _, _, files in os.walk(os.path.join(os.getcwd(), "extensions")):
            for file in files:
                if file.endswith(".py"):
                    reply_message = await self.load_extension(file[:-3], reply_message)

    async def reload_extension(self, extension_name: str, reply_message: Message) -> Message:
        message_content: str = reply_message.content

        print(f"Reloading extension: {extension_name}")
        await reply_message.edit(f"{message_content}\nReloading: {extension_name}")

        try:
            self.bot.reload_extension(f"extensions.{extension_name}")
            print(f"Reloaded extension: {extension_name}")
            await reply_message.edit(f"{message_content}\nReloaded: {extension_name}")
        except ExtensionNotLoaded:
            print(f"Failed to reload extension. Extension not loaded: {extension_name}")
            await reply_message.edit(f"{message_content}\nNot loaded: {extension_name}")
        except ExtensionNotFound:
            print(f"Failed to reload extension. Name not found: {extension_name}")
            await reply_message.edit(f"{message_content}\nNo such extension: {extension_name}")
        except (NoEntryPointError, ExtensionFailed) as exception:
            print(f"Failed to reload extension. Code failed to execute: {extension_name}")
            print(exception, file = sys.stderr, flush = True)
            await reply_message.edit(f"{message_content}\nCode error: {extension_name}")

    @group(name = "reload", invoke_without_command = True)
    @check(is_team_member)
    async def reload(self, ctx: Context, *extension_names: str) -> None:
        reply_message: Message = await ctx.reply(f"**Reloading {len(extension_names)} extensions:**\n")

        for name in extension_names:
            reply_message = await self.reload_extension(name, reply_message)

    @reload.command(name = "all")
    @check(is_team_member)
    async def reload_all(self, ctx: Context) -> None:
        reply_message: Message = await ctx.reply(f"**Reloading all extensions:**\n")

        for _, _, files in os.walk(os.path.join(os.getcwd(), "extensions")):
            for file in files:
                if file.endswith(".py"):
                    reply_message = await self.reload_extension(file[:-3], reply_message)


    async def unload_extension(self, extension_name: str, reply_message: Message) -> Message:
        message_content: str = reply_message.content

        print(f"Unloading extension: {extension_name}")
        await reply_message.edit(f"{message_content}\nUnloading: {extension_name}")

        try:
            self.bot.unload_extension(f"extensions.{extension_name}")
            print(f"Unloaded extension: {extension_name}")
            await reply_message.edit(f"{message_content}\nUnloaded: {extension_name}")
        except ExtensionNotLoaded:
            print(f"Failed to unload extension. Extension not loaded: {extension_name}")
            await reply_message.edit(f"{message_content}\nNot loaded: {extension_name}")
        except ExtensionNotFound:
            print(f"Failed to unload extension. Name not found: {extension_name}")
            await reply_message.edit(f"{message_content}\nNo such extension: {extension_name}")
        except (NoEntryPointError, ExtensionFailed) as exception:
            print(f"Failed to unload extension. Code failed to execute: {extension_name}")
            print(exception, file = sys.stderr, flush = True)
            await reply_message.edit(f"{message_content}\nCode error: {extension_name}")

    @group(name = "unload", invoke_without_command = True)
    @check(is_team_member)
    async def unload(self, ctx: Context, *extension_names: str) -> None:
        reply_message: Message = await ctx.reply(f"**Unloading {len(extension_names)} extensions:**\n")

        for name in extension_names:
            reply_message = await self.unload_extension(name, reply_message)

    @unload.command(name = "all")
    @check(is_team_member)
    async def unload_all(self, ctx: Context) -> None:
        reply_message: Message = await ctx.reply(f"**Unloading all extensions:**\n")

        for _, _, files in os.walk(os.path.join(os.getcwd(), "extensions")):
            for file in files:
                if file.endswith(".py"):
                    reply_message = await self.unload_extension(file[:-3], reply_message)