from openai import OpenAI
import parse_utils
import azure_utils
import context_utils
import json
import uuid


def completion(content: str) -> str:
    client = OpenAI()
    react_app = context_utils.get_react_app()
    print(f"React app {react_app}")

    query = f"""
    Use the following design document delimited by --- to build a Web application:

    ---
    {content}
    ---

    First identify the requirements for the application. Then build the complete implementation described below.

    The web application should have three parts: the frontend, the backend, and the database.

    Frontend instructions: Write the app frontend using React. Your output should be a complete app
    including all the files necessary to render the UI given the requirements.

    Backend instructions: Write the app backend using Kotlin and Ktor. The backend should start an HTTP server and define
    routes that handle the events defined in the Frontend given the requirements.

    Database instructions: Write SQL files to create the database schema. The tables should match the
    objects described in the requirements.

    Output all code files in one JSON structure. The structure should be a list of objects.
    Each object should have a "filename" attribute and a "contents" attribute.
    """

    print(f"Query: {query}")
    completion = client.chat.completions.create(
        model="o1-preview-2024-09-12",
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
