from typing import Dict

from openai import OpenAI
import jinja2


class OpenAIUtils:
    def __init__(self):
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader('/home/kiz/app/ai/openai/prompts'))

    def get_template_completion(self, template: str, template_params: Dict[str, str]) -> str:
        template = self.jinja.get_template(template)
        query = template.render(template_params)
        print(f"get_template_completion: {query}")
        client = OpenAI()
        completion = client.chat.completions.create(
            model="o1",
            store=False,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        completion_text = completion.choices[0].message.content
        print(f"completion: {completion_text}")
        return completion_text
