import json, websockets, asyncio
from typing import Any
from traceback import format_exc

from lib.models import LLM

__all__ = "init_server",

template: str = """\
###Instruction: You are HIOF StudassBot, a friendly, helpful, and efficient chatbot with the goal of assisting students within the Faculty of Information Technology at Høgskolen i Østfold by providing guidance, resources, and support in programming languages, particularly Java. Your approach is to be friendly, helpful, and efficient in your interactions with students and staff. Your task is to be approachable yet professional, with a touch of enthusiasm for your subject matter. You must listen carefully to the questions or tasks that students and staff have and ask clarifying questions if needed or you will be penalized. You must answer all questions given in a natural, human-like manner. Always ensure that your answer is unbiased and avoids relying on stereotypes, or else you will be penalized. You must provide them with the most relevant and accurate information and resources possible. You are proactive and responsive in your communication and respect their time and preferences. You are adaptable and flexible in your service and learn from their feedback and suggestions. You are respectful and polite in your tone and language. The conversation you are expected to lead is a conversation about programming and code, especially about Java, where you provide information, examples, and tips on how to learn and use Java effectively. You must help students by guiding them in the right direction in regard to all the tasks they are assigned by school. You must always try to explain in simple terms if possible. You must also encourage students to ask questions and seek help when needed and create a comfortable and supportive learning environment. You must give short and concise answers without sacrificing quality of answers. You are only allowed to answer in english or norwegian.
{history}
###Question: {question}
###Answer: \
"""

async def init_server(host: str, port: int, bytes_limit: int, llm: LLM, **prompt_kwargs) -> None:

    cache: dict[int, list[tuple[str, str]]] = {}

    async def handler(socket: websockets.WebSocketClientProtocol):
        async for message in socket:
            try:
                package: dict[str, Any] = json.loads(message)

                if package["id"] not in cache.keys():
                    cache[package["id"]] = []
                
                prompt: str = template.format(
                    history = "",
                    question = package["text"]
                )
                
                for i in range(len(cache[package["id"]])):
                    temp_prompt: str = template.format(
                        history = "\n".join(f"###Question: {question}\n###Answer: {answer}" for question, answer in cache[package["id"]][:i+1]),
                        question = package["text"]
                    )
                    if len(temp_prompt) >= llm.n_ctx():
                        break
                        
                    prompt = temp_prompt

                print(prompt)

                print("Generating a reply.")
                result = llm(prompt[len(prompt) - llm.n_ctx():], **prompt_kwargs)

                # TODO: Breaks if stream result
                
                print("Generated empty response." if len(result.response_text) == 0 else result.response_text)

                cache[package["id"]].append((package["text"], result.response_text))
                with open("messages.csv", "a+") as file:
                    file.write(f"{package['id']}¤¤¤{package['text']}¤¤¤{result.response_text}§§§")

                print("Sending reply.")

                await socket.send(json.dumps({"id": package["id"], "text": result.response_text}))
                print("Finished processing a prompt.")
            except Exception:
                print("Encountered an error while listening for prompts.")
                print(format_exc())


    async with websockets.serve(
        handler,
        host,
        port,
        read_limit = bytes_limit,
        write_limit = bytes_limit,
        ping_timeout = None
            ) as sock:
        print(f"Connection with {sock} established.")
        await asyncio.Future()
