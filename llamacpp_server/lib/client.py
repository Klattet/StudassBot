from socket import socket
from json import loads, JSONDecodeError
from typing import Any, TypeAlias, Union

from jsonschema import validate, ValidationError

__all__ = "prompt_send_receive",

Schema: TypeAlias = dict[str, Union[str, "Schema"]]

schema: Schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "text": {"type": "string"}
    },
    "additionalProperties": False
}

def prompt_send_receive(sock: socket, user_id: int, prompt: str) -> str:
    """
    Send prompt to server and expect a reply from LLM.
    Return the reply string.
    """

    try:
        sock.send(f'{{"id": {user_id}, "text": "{prompt}"}}'.encode(encoding = "utf-8"))

        received_data: bytes = sock.recv(4096)

        data: Any = loads(received_data)
        validate(data, schema)

        return data["text"]

    except UnicodeDecodeError:
        print("Data received was not correctly unicode encoded.")

    except JSONDecodeError:
        print("Data received was not correctly json encoded.")

    except ValidationError:
        print("Data received did not match the json schema.")

    except TimeoutError:
        print("Server did not respond.")
