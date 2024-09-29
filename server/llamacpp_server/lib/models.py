from typing import Iterator, Literal
from dataclasses import dataclass
from time import perf_counter
from itertools import chain

from llama_cpp import Llama, CreateCompletionResponse


__all__ = "StaticResult", "StreamResult", "LLM"


# Using a dataclass to save info about each LLM prompt run.
# Use slots for performance because there's no reason not to.
@dataclass(slots = True)
class StaticResult:
    model_id: str
    model_path: str
    prompt_text: str
    response_text: str
    prompt_token_count: int
    response_token_count: int
    total_token_count: int
    generation_time: float
    finish_reason: Literal["stop", "length"] | None

@dataclass(slots = True)
class StreamResult:
    model_id: str
    model_path: str
    prompt_text: str
    response_stream: Iterator[str]


class LLM(Llama):
    """
    A small wrapper class that makes the results output a bit nicer.
    """

    def __init__(self, model_path: str, **kwargs):
        super().__init__(model_path, **kwargs)

    def __call__(self, prompt: str, **kwargs) -> StaticResult | StreamResult:

        start: float = perf_counter()
        raw_result: CreateCompletionResponse | Iterator[CreateCompletionResponse] = super().__call__(prompt, **kwargs)
        stop: float = perf_counter()

        if isinstance(raw_result, dict):
            return StaticResult(
                model_id = raw_result["id"],
                model_path = raw_result["model"],
                prompt_text = prompt,
                response_text = raw_result["choices"][0]["text"],
                prompt_token_count = raw_result["usage"]["prompt_tokens"],
                response_token_count = raw_result["usage"]["completion_tokens"],
                total_token_count = raw_result["usage"]["total_tokens"],
                generation_time = stop - start,
                finish_reason = raw_result["choices"][0]["finish_reason"]
            )
        else:
            first: CreateCompletionResponse = next(raw_result)
            return StreamResult(
                model_id = first["id"],
                model_path = first["model"],
                prompt_text = prompt,
                response_stream = chain((first["choices"][0]["text"],), (e["choices"][0]["text"] for e in raw_result))
            )
