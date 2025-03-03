from openai import OpenAI
import parse_utils
import azure_storage
import json
import uuid


def completion(content: str) -> str:
    client = OpenAI()

    query = f"""
    Use the following design document to create a Web application:

    {content}

    Build the app frontend using React. Build the app backend using Kotlin and Ktor.
    Create a database schema using Postgres.

    The app frontend event handlers should post to the backend routes defined in Ktor.
    The backend server routes to save data in the Postgres database.

    Output all code files in one JSON structure. The structure should be a list of objects.
    Each object should have a "filename" attribute and a "contents" attribute.
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

    blob_dir = uuid.uuid4()
    for file_list in parse_utils.extract_all_json_blocks(completion_text):
        for f in file_list:
            filename = f['filename']
            contents = f['contents']
            blob = f"{blob_dir}/{filename}"
            print(f"Uploading: {contents} {blob}")
            azure_storage.upload_json_blob(contents, blob)

    return completion_text
