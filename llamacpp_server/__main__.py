import asyncio

from llamacpp_server.lib import LLM, init_server

llm_path = "CHANGE ME"

def main() -> None:

    llm = LLM(llm_path, n_gpu_layers = -1, n_ctx = 1024, n_batch = 256, stop = "###")

    asyncio.run(init_server("localhost", 8899, 65536, llm, max_tokens = 512, top_p = 0.15, temperature = 0.35))


if __name__ == "__main__":
    main()
