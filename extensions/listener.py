import tomllib, json, websockets
from typing import Any
from traceback import format_exc

from disnake import Message, Event
from disnake.ext.commands import Cog, Bot, Context

__all__ = ()

def setup(bot: Bot) -> None:
    bot.add_cog(Listener(bot))

class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

        with open("config.toml", "rb") as config_file:
            config = tomllib.load(config_file)

        self.server_ip: str = config["server_ip"]
        self.port: int = config["port"]
        self.bytes_limit: int = config["bytes_limit"]

        self.socket: websockets.WebSocketClientProtocol | None = None

        self.waiting_list: dict[int, tuple[Message, Message]] = {}

    @Cog.listener(Event.ready)
    async def connect(self) -> None:
        while True:
            try:
                print(f"Attempting to connect to LLM server at {self.server_ip}:{self.port}")
                self.socket = await websockets.connect(
                    f"ws://{self.server_ip}:{self.port}",
                    write_limit = self.bytes_limit,
                    read_limit = self.bytes_limit,
                    ping_timeout = None
                )
                print("Connected successfully.")
                await self.send()
            except Exception as e:
                print("Encountered an error while listening for prompts.")
                print(format_exc())
                await self.socket.close()
                await self.socket.wait_closed()

    @Cog.listener(Event.message)
    async def listen(self, message: Message) -> None:
        """
        Listens to messages in private messages to respond to.
        """

        # Filter messages to only relevant ones.
        context: Context = await self.bot.get_context(message)
        if message.author.bot or message.guild or context.command: return

        if message.author.id in self.waiting_list.keys():
            await message.reply("Please wait until reply has finished generating before sending more messages.")
            return

        print("Received a prompt.")

        self.waiting_list[message.author.id] = (message, await message.reply("Please wait while reply is being generated.", mention_author = False))

        try:
            print("Sending prompt to LLM server.")
            await self.socket.send(json.dumps({"id": message.author.id, "text": message.content}))

        except Exception as e:
            _, temporary = self.waiting_list.pop(message.author.id)
            await temporary.delete()
            await message.reply("Something went wrong.", mention_author = False)
            print("Error encountered.")
            print(format_exc())

    async def send(self) -> None:

        print("Waiting for responses.")

        async for message in self.socket:
            package: dict[str, Any] = json.loads(message)
            print("Received response.")

            original, temporary = self.waiting_list.pop(package["id"])

            await temporary.delete()
            
            if len(package["text"].strip()) == 0:
                print("Empty response received.") 
                await original.channel.send("I'm sorry, I could not find a response to that.")
            
            elif len(package["text"]) <= 2000:
                print("Short response received.")
                await original.channel.send(package["text"])
            
            else:
                print("Long response received.")
                n_messages: int = len(package["text"]) // 2000 + 1
                n_character_per: int = len(package["text"]) // n_messages

                for i in range(n_messages):
                    msg = package["text"][i * n_character_per:i * n_character_per + n_character_per]
                    if len(msg) != 0:
                        await original.channel.send(msg)
