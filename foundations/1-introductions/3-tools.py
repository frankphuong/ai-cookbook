from enum import Enum
from openai import OpenAI
from pydantic import BaseModel


client = OpenAI(base_url="http://localhost:11434/v1", api_key="")


class Request(str, Enum):
    POLICY = "policy"
    WARRANTY = "warranty"
    SALES = "sales"


def get_available_employee(request):
    """Phân loại thông tin user yêu cầu và gửi về cho nhân viên"""
    employees = [
        {"name": "Frank", "role": "policy and warranty specialist"},
        {"name": "Elaine", "role": "product specialist"},
    ]

    if request in [Request.POLICY, Request.WARRANTY]:
        return employees[0]["name"]
    else:
        return employees[1]["name"]


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_available_employee",
            "description": "Phân công nhân viên phù hợp xử lý yêu cầu của khách hàng",
            "parameters": {
                "type": "objects",
                "properties": {"request": {"type": "string"}},
                "required": ["request"],
                "addititopiconalProperties": False,
            },
            "strict": True,
        },
    }
]


class TicketPriority(Enum):
    HIGH = "high"
    LOW = "low"


class UserTicket(BaseModel):
    username: str
    raw_request: str
    classify_request: Request
    summary_information: str
    product_name: str
    priority: TicketPriority
    empoyee_name: str


completions = client.chat.completions.parse(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": """
Bạn là trợ lý ảo chăm sóc và trả lời thông tin khách hàng.
Dựa vào yêu cầu của khách hàng, hãy trích xuất thông tin theo format""",
        },
        {
            "role": "user",
            "content": "Tôi đang sử dụng sản phẩm A nhưng bị lỗi phần mềm. Tôi đang rất gấp. Bạn có thể xử lý cho tôi không?",
        },
    ],
    response_format=UserTicket,
    tools=tools,
)

completions.model_dump()


def call_function(name, args):
    if name == "get_available_employee":
        return get_available_employee(**args)


print(completions.choices[0].message)
# for tool_call in completions.choices[0].message.tool_calls:
#     name = tool_call.function.name
#     print(name)


# response = completions.choices[0].message

# print(response.content)
