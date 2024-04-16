import tomllib
from socket import socket, AF_INET, SOCK_STREAM
from typing import Any
from json import loads, JSONDecodeError

from disnake import Message
from disnake.ext.commands import Cog, Bot, Context
from jsonschema import validate, ValidationError

__all__ = ()

type Schema = dict[str, str | Schema]

schema: Schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "text": {"type": "string"}
    }
}

def setup(bot: Bot) -> None:
    bot.add_cog(Listener(bot))

class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

        with open("config.toml", "rb") as config_file:
            config = tomllib.load(config_file)

        self.socket = self.establish_connection(config["server_ip"], config["port"])

    @staticmethod
    def establish_connection(host: str, port: int) -> socket:
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def prompt_send_receive(self, user_id: int, prompt: str) -> str:
        """
        Send prompt to server and expect a reply from LLM.
        Return the reply string.
        """

        try:
            self.socket.send(f'{{"id": {user_id}, "text": "{prompt}"}}'.encode(encoding = "utf-8"))

            received_data: bytes = self.socket.recv(4096)

            data: Any = loads(received_data)
            validate(data, schema)

            return data["text"]

        except UnicodeDecodeError:
            print("Data received was not correctly unicode encoded.")
            return "Something went wrong."

        except JSONDecodeError:
            print("Data received was not correctly json encoded.")
            return "Something went wrong."

        except ValidationError:
            print("Data received did not match the json schema.")
            return "Something went wrong."

        except TimeoutError:
            print("Server did not respond.")
            return "Something went wrong."

    @Cog.listener("on_message")
    async def listener(self, message: Message) -> None:
        """
        Listens to messages in private messages to respond to.
        """

        # Filter messages to only relevant ones.
        context: Context = await self.bot.get_context(message)
        if message.author.bot or message.guild or context.command: return

        await message.channel.send(self.prompt_send_receive(message.author.id, message.content))
