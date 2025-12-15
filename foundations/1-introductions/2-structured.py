from enum import Enum

from openai import OpenAI
from pydantic import BaseModel


client = OpenAI(base_url="http://localhost:11434/v1", api_key="")


class TicketPriority(str, Enum):
    HIGH: str = "high"
    LOW: str = "low"


class UserTicket(BaseModel):
    username: str
    raw_request: str
    summary_information: str
    product_name: str
    priority: TicketPriority


completions = client.chat.completions.parse(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": """Bạn là trợ lý ảo chăm sóc và trả lời thông tin khách hàng.
Dựa vào yêu cầu của khách hàng để tạo ra user ticket (Bao gồm các thông tin được phân nhóm).""",
        },
        {
            "role": "user",
            "content": "Tôi đang sử dụng sản phẩm A nhưng bị lỗi phần mềm. Tôi đang rất gấp. Bạn có thể xử lý cho tôi không?",
        },
    ],
    response_format=UserTicket,
)


response = completions.choices[0].message

print(response.content)
