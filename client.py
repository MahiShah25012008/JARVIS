import os
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[
        {
            "role": "system",
            "content": "You are a virtual assistant named Jarvis."
        },
        {
            "role": "user",
            "content": "What is coding?"
        }
    ]
)

print(completion.choices[0].message.content)
