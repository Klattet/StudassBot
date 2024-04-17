import tomllib, json, asyncio, re
from socket import socket, AF_INET, SOCK_STREAM
from typing import Any, TypeAlias, Union
from traceback import format_exc

from disnake import Message
from disnake.ext.commands import Cog, Bot, Context
from jsonschema import validate

__all__ = ()

Schema: TypeAlias = dict[str, Union[str, "Schema"]]

schema: Schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "text": {"type": "string"}
    },
    "additionalProperties": False
}

def setup(bot: Bot) -> None:
    bot.add_cog(Listener(bot))

class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

        self.socket: socket | None = None
        self.is_connecting: bool = False

        with open("config.toml", "rb") as config_file:
            config = tomllib.load(config_file)

        self.server_ip: str = config["server_ip"]
        self.port: int = config["port"]
        self.bytes_limit: int = config["bytes_limit"]

        self.translator: dict[int, str] = str.maketrans({"\"": "\\\""})

    @Cog.listener("on_ready")
    async def connect(self) -> None:
        """
        Establish a connection to the LLM server.
        """

        self.is_connecting = True

        while True:
            try:
                self.socket = socket(AF_INET, SOCK_STREAM)

                print(f"Attempting to connect to LLM server at {self.server_ip}:{self.port}")
                self.socket.connect((self.server_ip, self.port))
                self.is_connecting = False
                print("Connected successfully.")
                return

            except Exception as e:
                print("Encountered exception while trying to connect to LLM server.")
                print(format_exc())
                print("Retrying in 15 seconds.")
                await asyncio.sleep(15)

    @property
    def is_connected(self) -> bool:
        return self.socket is not None and self.socket.fileno() != -1

    @Cog.listener("on_message")
    async def listener(self, message: Message) -> None:
        """
        Listens to messages in private messages to respond to.
        """

        # Filter messages to only relevant ones.
        context: Context = await self.bot.get_context(message)
        if message.author.bot or message.guild or context.command: return

        print("Received a prompt.")

        temporary_message: Message = await message.channel.send("Please wait while reply is being generated.")

        try:

            assert self.is_connected and not self.is_connecting

            print("Sending prompt to LLM server.")

            reply_bytes: bytes = message.content.encode(encoding = "utf-8")

            assert len(reply_bytes) <= self.bytes_limit

            self.socket.sendall(reply_bytes)

            print("Waiting on reply.")
            received_data: bytes = self.socket.recv(self.bytes_limit)

            assert received_data != b""

            reply_message: str = received_data.decode(encoding = "utf-8")

            n_messages: int = len(reply_message) // 2000 + 1
            n_character_per: int = len(reply_message) // n_messages

            for i in range(n_messages):
                await message.channel.send(reply_message[i:i+n_character_per])

            print("Finished processing a prompt.")

        except Exception as e:
            print("Encountered an error while listening for prompts.")
            print(format_exc())
            await message.channel.send("Something went wrong.")

            if not self.is_connected and not self.is_connecting:
                print("Attempting to reconnect.")
                await self.connect()

        await temporary_message.delete()
