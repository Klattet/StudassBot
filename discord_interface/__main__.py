import tomllib
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
    bot.load_extensions("extensions")

    print("Starting.")
    bot.run(config["api_key"])

if __name__ == "__main__":
    main()