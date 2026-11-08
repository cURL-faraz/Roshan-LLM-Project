"""Task 3 smoke test: one real OpenRouter call. Run from the project root:  python -m scripts.smoke_llm"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openrouter.errors import OpenRouterError
from rag.llm import build_chat_model

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"  


def main() -> None:
    load_dotenv(ENV_FILE)
    try:
        api_key = os.environ["OPENROUTER_API_KEY"]
    except KeyError:
        raise RuntimeError("The API key is missing.") from None
    try:
        model_name = os.environ["OPENROUTER_MODEL"]
    except KeyError:
        raise RuntimeError("The model is missing.") from None
    timeout = float(os.environ.get("OPENROUTER_TIMEOUT", 60))

    model = build_chat_model(model_name, api_key, timeout)
    start = time.perf_counter()
    response = model.invoke("سلام دارم برای اولین بار از اوپن روتر استفاده می کنم!")
    latency = time.perf_counter() - start
    usage = response.usage_metadata or {}
    print("=== Success path ===")
    print(f"Model    : {response.response_metadata.get('model_name', model_name)}")
    print(f"Latency  : {latency:.2f} s")
    print(f"Tokens   : input={usage.get('input_tokens')} output={usage.get('output_tokens')} total={usage.get('total_tokens')}")
    print(f"Answer   :\n{response.content}\n")
    print("=== Failure path (invalid key) ===")
    invalid_model = build_chat_model(model_name, "invalid", timeout)
    try:
        invalid_model.invoke("سلام دارم برای اولین بار از اوپن روتر استفاده می کنم!")
    except OpenRouterError as exc:
        print(f"Caught   : {type(exc).__name__} (expected UnauthorizedResponseError)")
    else:
        print("Unexpected: the invalid key was accepted")


if __name__ == "__main__":
    main()
