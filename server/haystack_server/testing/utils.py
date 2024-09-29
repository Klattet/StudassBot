import traceback, sys, gc, json
from typing import Generator, Any

from lib import LLM
from server.haystack_server.testing import LLMTester

__all__ = "test_model_dump", "test_models_dump", "parse_tps", "print_sorted_tps", "parse_responses", "print_responses"

def test_model_dump(llm: LLM, dump_path: str, prompt_template: str, prompt: str, run_count: int) -> None:
    try:
        tester = LLMTester(llm)
        tester.run_n(run_count, prompt_template, prompt)
        tester.dump_all(dump_path)
    except Exception:
        print(traceback.format_exc(), file = sys.stderr)

def test_models_dump(llm_generator: Generator[LLM, None, None], dump_path: str, prompt_template: str, prompt: str, run_count: int):
    for llm in llm_generator:
        test_model_dump(llm, dump_path, prompt_template, prompt, run_count)
        gc.collect()

def parse_tps(data_path: str) -> dict[str, float]:
    with open(data_path, "r") as file:
        data_dict: dict[str, Any] = json.load(file)

    tps_dict: dict[str, float] = {}

    for model, results in data_dict.items():
        tps_dict[model] = sum(result["token_count"] / result["generation_time"] for result in results) / len(results)

    return tps_dict

def print_sorted_tps(tps_data: dict[str, float]) -> None:

    sorted_tps: list[tuple[str, Any]] = sorted(((k, v) for k, v in tps_data.items()), key = lambda e: e[1], reverse = True)

    for model, tps in sorted_tps:
        print(f"{model:50} | Average tps: {tps:.3f}")

def parse_responses(data_path: str) -> dict[str, list[str]]:
    with open(data_path, "r") as file:
        data_dict: dict[str, Any] = json.load(file)

    response_dict: dict[str, list[str]] = {}

    for model, results in data_dict.items():
        response_dict[model] = []
        for result in results:
            response_dict[model].append(result["response"])

    return response_dict

def print_responses(response_data: dict[str, list[str]]) -> None:
    for model, responses in response_data.items():
        print(f"{model}:")
        for num, response in enumerate(responses, start = 1):
            print(f"\tResponse {num}:")
            for line in response.splitlines():
                print(f"\t\t{line}")
        print()
