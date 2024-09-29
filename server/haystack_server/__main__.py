from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import Document

from server.parsing import parse_directory
from lib import LLamaCpp, LLMResult

prompt_template = """\
You are a student assistant. You must answer in a way that helps students arrive at the correct answer themselves.
The students are all programming and software engineer students. You will never give a direct solution to students' tasks.
Help the student learn in a way that is natural for a human conversation.

Using the following documents answer the question:

{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Student question: I need help with a task for school. {{prompt}}

Answer: \
"""

prompt = "How can I create a class in Java that represents a celestial body, and create subclasses that represent things like planets and moons?"

document_directory: str
llm_path: str = "D:/LLM/orca-2-7b.Q4_K_M.gguf"

def main() -> None:

    # Laste inn all fagstoff data
    documents: list[Document] = []
    for file_path, text in parse_directory(document_directory).items():
        documents.append(Document(id = file_path, content = text))

    document_store = InMemoryDocumentStore()
    document_store.write_documents(documents = documents)

    llm = LLamaCpp(llm_path, model_kwargs = {"n_gpu_tokens": -1, "n_ctx": 500})

    result: LLMResult = llm.run_with_bm25(
        prompt_template = prompt_template,
        prompt = prompt,
        document_store = document_store,
        generation_kwargs = {"max_tokens": 300}
    )


    print(result.prompt)

    print(result.response)

def main2() -> None:

    llm = LLamaCpp(llm_path, model_kwargs = {"n_gpu_tokens": -1, "n_ctx": 500})

    result: LLMResult = llm.run(
        prompt_template = prompt_template,
        prompt = prompt,
        generation_kwargs = {"max_tokens": 300}
    )


    print(result.prompt)

    print(result.response)

if __name__ == "__main__":
    main2()