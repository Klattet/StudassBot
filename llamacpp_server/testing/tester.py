import dataclasses, os, json
from typing import Any

from ..lib import LLM, StaticResult, StreamResult

__all__ = "LLMTester",

class LLMTester:
    """
    A class used to performance test an LLM.
    Caches results from consecutive runs to parse useful data from the results.
    """

    __slots__ = "llm", "_test_cache"

    def __init__(self, llm: LLM) -> None:
        self.llm: LLM = llm

        self._test_cache: list[StaticResult | StreamResult] = []

    def reset(self) -> None:
        self._test_cache.clear()

    @property
    def test_cache(self) -> list[StaticResult | StreamResult]:
        return self._test_cache

    @property
    def model_name(self) -> str:
        return os.path.basename(self.llm.model_path)

    @property
    def responses(self) -> tuple[str, ...]:
        return tuple(result.response_text for result in self._test_cache)

    @property
    def tokens_per_second(self) -> tuple[float, ...]:
        return tuple(result.token_count / result.generation_time for result in self._test_cache)

    @property
    def average_tokens_per_second(self) -> float:
        return sum(self.tokens_per_second) / len(self._test_cache)

    def run(self, *args, **kwargs) -> None:
        self._test_cache.append(self.llm.run(*args, **kwargs))

    def run_n(self, run_count: int, *args, **kwargs) -> None:
        for _ in range(run_count):
            self.run(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {self.model_name: list(map(dataclasses.asdict, self.test_cache))}

    def dump_all(self, file_path: str) -> None:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                file_data = json.load(file)
        else:
            file_data = {}

        file_data.update(self.to_dict())

        with open(file_path, "w+") as file:
            json.dump(file_data, file, indent = 4, skipkeys = True)

    def dump_average_tps(self, file_path: str) -> None:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                file_data = json.load(file)
        else:
            file_data = {}

        file_data.update({self.model_name: self.average_tokens_per_second})

        with open(file_path, "w+") as file:
            json.dump(file_data, file, indent = 4, skipkeys = True)

    def dump_format_responses(self, file_path: str) -> None:
        with open(file_path, "a+") as file:
            file.write(f"{self.model_name}:\n")
            for num, result in enumerate(self._test_cache, start = 1):
                file.write(f"\tResponse {num}:\n")
                for line in result.response.splitlines():
                    file.write(f"\t\t{line}\n")