import tomllib, os
from typing import Any

from disnake import Intents
from disnake.ext.commands import Bot

from lib import get_prefix

def main() -> None:

    with open("config.toml", "rb") as config_file:
        config: dict[str, Any] = tomllib.load(config_file)

    bot = Bot(
        command_prefix = get_prefix(config["default_prefix"]),
        case_insensitive = True,
        strip_after_prefix = True,
        intents = Intents.all(), # Must change this when specifics about the bot are known.
    )

    # Wonky workaround for loading the extensions while running the program from the outer project directory.
    # Silly __main__.py moment. Might do a pull request for disnake later to make it easier.
    # IF YOU'RE CONFUSED: Run the program like `python discord_interface` from the StudassBot directory as if the folder itself is the main file.
    program_path: str = os.path.join(os.getcwd(), "discord_interface")
    for path, subdirs, files in os.walk(os.path.join(program_path, "extensions")):
        for name in files:
            if name.endswith(".py"):
                bot.load_extension(f"extensions.{name[:-3]}", package = program_path)

    print("Starting.")
    bot.run(config["api_key"])

if __name__ == "__main__":
    main()