from openai import OpenAI
import parse_utils
import azure_utils
import context_utils
import uuid
import jinja2


class MainAgent:
    def __init__(self):
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader('/home/kiz/app/ai/openai/prompts'))

    def get_completion(self, content: str) -> str:
        client = OpenAI()
        react_app = context_utils.get_react_app()
        print(f"React app {react_app}")

        template = self.jinja.get_template("frontend.prompt")
        query = template.render(user_requirements=content)

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

agent = MainAgent()
agent.get_completion("this is my openai query")