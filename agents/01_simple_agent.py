import json
import pprint
import re

from typing import Any, Callable, Dict, List

from openai import OpenAI
from utils.config import settings


class Agent:
    def __init__(
        self,
        name: str = "Agent",
        instruction: str = "",
        model: str = "gemma4:cloud",
        max_steps: int = 4,
        client: OpenAI | None = None,
    ):
        self._name = name
        self._instruction = instruction or "You're an useful assistant"
        self._max_steps = max_steps
        self._base_url = settings.active.base_url or "http://localhost:11434/v1"
        self._api_key = settings.active.api_key or "ollama"
        self._model = model or settings.active.default_model or "gema4:cloud"
        self._client = client or OpenAI(base_url=self._base_url, api_key=self._api_key)
        self._memory: List[Any] = []
        self._tool_specs: List[Dict[Any, Any]] = []
        self._tool_fns: Dict[str, Callable[..., Any]] = {}

    def add_tools(
        self,
        fn: Callable[..., Any],
        description: str,
        parameters: Dict[str, Any],
        strict: bool,
    ) -> None:
        self._tool_specs.append(
            {
                "type": "function",
                "name": fn.__name__,
                "description": description,
                "parameters": parameters,
                "strict": strict,
            }
        )

        self._tool_fns[fn.__name__] = fn

    def _call_tool(self, name: str, arguments: str) -> str:
        fn = self._tool_fns.get(name)
        if fn is None:
            return f"Tool {name} not found"
        try:
            result = fn(**json.loads(arguments or "{}"))
            if isinstance(result, str):
                return result
            else:
                return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Catch error {e}"

    def run(self, user_message: str, verbose: bool = True) -> str:
        self._memory.append({"role": "user", "content": user_message})

        for step in range(1, self._max_steps + 1):
            response = self._client.responses.create(
                model=self._model,
                instructions=self._instruction,
                input=self._memory,
                tools=self._tool_specs or None,
            )

            self._memory += response.output

            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                return response.output_text

            for call in tool_calls:
                if verbose:
                    print(
                        f"[step {step}] {self._name} call tool: {call.name}({call.arguments})"
                    )
                output = self._call_tool(call.name, call.arguments)
                self._memory.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": output,
                    }
                )

        return "Reached max_steps but don't have the answer"

    def reset(self) -> None:
        self._memory.clear()


# ========== Tools ===========
def get_product_info(product_name: str) -> Dict[str, Any]:
    if re.search("|".join(["apple", "Apple", "macbook", "Macbook"]), product_name):
        return {
            "product_id": "macbook-pro-14-m1",
            "name": "Macbook Pro 14 inch M1",
            "price": 20000000,
            "currency_unit": "vnd",
            "brand": "Apple",
        }
    else:
        return {
            "product_id": "Keyboard",
            "name": "Logitech keyboard",
            "price": 100000,
            "currency_unit": "vnd",
            "brand": "Apple",
        }


def get_quantity_at_store(product_id: str, store_id: int):
    if store_id != 1:
        return "Store not found"
    elif store_id == 1 and product_id == "macbook-pro-14-m1":
        return {"store_id": 1, "product_id": "macbook-pro-14-m1", "quantity": 100}
    else:
        return "Product not found"


if __name__ == "__main__":
    agent = Agent(
        name="Store agent",
        instruction="""
            You're a storage agent.
            You manage product's quantity of my store.
            Use tools to access information and quantity if I need to know.
        """,
    )

    agent.add_tools(
        fn=get_product_info,
        description="Find information about product base on product name",
        parameters={
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Product's name"}
            },
            "required": ["product_name"],
        },
        strict=False,
    )

    agent.add_tools(
        fn=get_quantity_at_store,
        description="Get specific product's quantity at specific store",
        parameters={
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product's id"},
                "store_id": {"type": "number", "description": "Store's id"},
            },
            "required": ["product_id", "store_id"],
        },
        strict=False,
    )

    print(agent.run("I need to know how many pices of Macbook at store 1"))
