from openai import OpenAI
import parse_utils
import json


def completion(content: str) -> str:
    client = OpenAI()

    query = f"""
    Use the following design document to create a Web application:

    {content}

    Write the frontend in React. Write the backend server using Ktor.

    Output all code files in one JSON structure. The structure should be a list of objects. Each object should have a filename attribute and a contents attribute.
    """

    print(f"Query: {query}")
    completion = client.chat.completions.create(
        model="gpt-4o",
        store=True,
        messages=[
            {"role": "user", "content": query}
        ]
    )
    print(f"Completion: {completion}")
    completion_text = completion.choices[0].message.content

    for code in parse_utils.extract_all_json_blocks(completion_text):
        print(f"Code: {json.dumps(code, indent=2)}")
    return completion_text
