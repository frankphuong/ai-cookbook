from openai import OpenAI


client = OpenAI(base_url="http://localhost:11434/v1", api_key="")


completion = client.chat.completions.create(
    model="deepseek-r1:8b",
    messages=[
        {
            "role": "system",
            "content": "Bạn là một trợ lý trả lời các câu hỏi chăm sóc khách hàng. Hãy trả lời câu hỏi ngắn gọn, không dài dòng",
        },
        {
            "role": "user",
            "content": "Bạn là ai? Có nhiệm vụ gì?",
        },
    ],
)

response = completion.choices[0].message

print(response.content)
