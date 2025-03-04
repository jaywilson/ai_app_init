from openai import OpenAI
import parse_utils
import azure_utils
import json
import uuid


def completion(content: str) -> str:
    client = OpenAI()

    query = f"""
    Use the following design document to create a Web application:

    {content}

    Write the app frontend using React. The frontend should include

    Write the app server using Kotlin and Ktor. The server should be based on the exact directory
    and file contents output by "gradle init".

    The app frontend event handlers should post to the backend routes defined in Ktor.
    The backend server routes should save data in a Postgres database with the required schema.

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
            try:
                filename = f['filename']
                contents = f['contents']
                blob = f"{blob_dir}/{filename}"
                print(f"Uploading: {contents} {blob}")
                azure_utils.upload_json_blob(contents, blob)
            except Exception as e:
                print(f"Error: {str(e)} File: {f}")

    return completion_text
