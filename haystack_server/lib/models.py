from typing import Any, Self, Sequence
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from time import perf_counter

from haystack.dataclasses import Document
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

__all__ = "LLMResult", "LLM", "LLamaCpp"

# Using a dataclass to save info about each LLM prompt run.
# Use slots for performance because there's no reason not to.
@dataclass(slots = True)
class LLMResult:
    prompt: str
    response: str
    token_count: int
    generation_time: float
    stop_reason: str

    #llm_path: str
    #llm_type: type["LLM"]
    #model_kwargs: dict[str, Any]
    #generation_kwargs: dict[str, Any]


type SupportedGenerator = (
    LlamaCppGenerator
)
supported_generators: tuple[type] = (
    LlamaCppGenerator,
)

class LLM(metaclass = ABCMeta):
    """
    A metaclass that other LLM wrappers must inherit from.
    Serves as a factory class if you just want to pass in a Haystack Generator without worrying about it.
    The Generator must be in supported_generators for the factory to work.
    """

    __slots__ = "generator", "model_path"

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """
        Takes the same arguments as the Haystack Generator.
        """
        ...

    @classmethod
    @abstractmethod
    def from_generator(cls, generator: SupportedGenerator) -> Self:
        if type(generator) not in supported_generators:
            raise ValueError(f"Generator type {type(generator)} is not supported.")

        if isinstance(generator, LlamaCppGenerator):
            return LLamaCpp.from_generator(generator)

    @abstractmethod
    def run(self, prompt_template: str, prompt: str, generation_kwargs: dict[str, Any] | None = None) -> LLMResult:
        """
        prompt_template: A string that uses the Jinja2 formatting like in Haystack. {{prompt}} marks the location of the prompt input.
        prompt: The prompt input in pure text.
        generation_kwargs: The specific model's generation keyword arguments.
        """
        ...

    @abstractmethod
    def run_with_docs(self, prompt_template: str, prompt: str, documents: Sequence[Document], generation_kwargs: dict[str, Any] | None = None) -> LLMResult:
        """
        prompt_template: A string that uses the Jinja2 formatting like in Haystack. {{prompt}} marks the location of the prompt input.
        prompt: The prompt input in pure text.
        documents: The documents to include in the prompt.
        generation_kwargs: The specific model's generation keyword arguments.
        """
        ...

    @abstractmethod
    def run_with_bm25(self, prompt_template: str, prompt: str, document_store: InMemoryDocumentStore, document_count: int = 3, generation_kwargs: dict[str, Any] | None = None) -> LLMResult:
        """
        prompt_template: A string that uses the Jinja2 formatting like in Haystack. {{prompt}} marks the location of the prompt input.
        prompt: The prompt input in pure text.
        document_store: In memory document store to search for relevant info in.
        generation_kwargs: The specific model's generation keyword arguments.
        """
        ...

class LLamaCpp(LLM):

    __slots__ = "generator", "model_path"

    def __init__(self, *args, **kwargs) -> None:
        self.generator: LlamaCppGenerator = LlamaCppGenerator(*args, **kwargs)
        self.model_path: str = self.generator.model_path

        self.generator.warm_up()

    @classmethod
    def from_generator(cls, generator: LlamaCppGenerator) -> Self:
        self = object.__new__(cls)
        self.generator = generator
        self.model_path = self.generator.model_path

        self.generator.warm_up()
        return self

    def run(self, prompt_template: str, prompt: str, generation_kwargs: dict[str, Any] | None = None) -> LLMResult:

        prompt_builder = PromptBuilder(prompt_template)
        new_prompt: str = prompt_builder.run(prompt = prompt)["prompt"]

        start: float = perf_counter()
        result: dict[str, list] = self.generator.run(new_prompt, generation_kwargs)
        stop: float = perf_counter()

        return LLMResult(
            prompt = prompt,
            response = result["replies"][0],
            token_count = result["meta"][0]["usage"]["completion_tokens"],
            generation_time = stop - start,
            stop_reason = result["meta"][0]["choices"][0]["finish_reason"]

            #llm_path = result["meta"][0]["model"],
            #llm_type = self.__class__,
            #model_kwargs = dict((f, getattr(self.generator.model.model_params, f)) for f, _ in self.generator.model.model_params._fields_),
            #generation_kwargs = dict((f, getattr(self.generator.model.context_params, f)) for f, _ in self.generator.model.context_params._fields_)
        )

    def run_with_docs(self, prompt_template: str, prompt: str, documents: Sequence[Document], generation_kwargs: dict[str, Any] | None = None) -> LLMResult:

        prompt_builder = PromptBuilder(prompt_template)
        new_prompt: str = prompt_builder.run(prompt = prompt, documents = documents)["prompt"]

        start: float = perf_counter()
        result: dict[str, list] = self.generator.run(new_prompt, generation_kwargs)
        stop: float = perf_counter()

        return LLMResult(
            prompt = prompt,
            response = result["replies"][0],
            token_count = result["meta"][0]["usage"]["completion_tokens"],
            generation_time = stop - start,
            stop_reason = result["meta"][0]["choices"][0]["finish_reason"]

            # llm_path = result["meta"][0]["model"],
            # llm_type = self.__class__,
            # model_kwargs = dict((f, getattr(self.generator.model.model_params, f)) for f, _ in self.generator.model.model_params._fields_),
            # generation_kwargs = dict((f, getattr(self.generator.model.context_params, f)) for f, _ in self.generator.model.context_params._fields_)
        )

    def run_with_bm25(self, prompt_template: str, prompt: str, document_store: InMemoryDocumentStore, document_count: int = 3, generation_kwargs: dict[str, Any] | None = None) -> LLMResult:

        document_retriever = InMemoryBM25Retriever(document_store)
        relevant_documents: list[Document] = document_retriever.run(query = prompt, top_k = document_count)["documents"]

        #print(relevant_documents[0].id)

        prompt_builder = PromptBuilder(prompt_template)
        new_prompt: str = prompt_builder.run(prompt = prompt, documents = relevant_documents)["prompt"]

        start: float = perf_counter()
        result: dict[str, list] = self.generator.run(new_prompt, generation_kwargs)
        stop: float = perf_counter()

        return LLMResult(
            prompt = prompt,
            response = result["replies"][0],
            token_count = result["meta"][0]["usage"]["completion_tokens"],
            generation_time = stop - start,
            stop_reason = result["meta"][0]["choices"][0]["finish_reason"]

            # llm_path = result["meta"][0]["model"],
            # llm_type = self.__class__,
            # model_kwargs = dict((f, getattr(self.generator.model.model_params, f)) for f, _ in self.generator.model.model_params._fields_),
            # generation_kwargs = dict((f, getattr(self.generator.model.context_params, f)) for f, _ in self.generator.model.context_params._fields_)
        )