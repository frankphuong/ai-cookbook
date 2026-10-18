import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL")
API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL = os.getenv("OLLAMA_DEFAULT_MODEL") or "gema4:cloud"

if __name__ == "__main__":
    prompt = "What is AI agent?"
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    response = client.responses.create(
        model=MODEL, input=[{"role": "user", "content": prompt}]
    )
    print(response.output_text)
