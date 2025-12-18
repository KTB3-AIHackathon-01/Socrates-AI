# AWS Bedrock
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "당신에 대해 설명해줘요"}
    ]
)

print(response)