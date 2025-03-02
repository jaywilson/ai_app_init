from openai import OpenAI


def completion(content: str) -> str:
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        store=True,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content
