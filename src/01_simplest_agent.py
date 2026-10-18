import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL")
API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL = os.getenv("OLLAMA_DEFAULT_MODEL") or "qwen3:8b"


def main():
    print(BASE_URL)
    print(API_KEY)
    print(MODEL)
    agent = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    prompt = (
        "What is AI agent? What is the different between AI agent and durable agent?"
    )
    response = agent.responses.create(
        model=MODEL, input=[{"role": "user", "content": prompt}]
    )
    print(response.output_text)


main()
