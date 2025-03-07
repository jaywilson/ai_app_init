from typing import Dict, List, Any

from openai import OpenAI
import jinja2
import utils


class Conversation:
    def __init__(self):
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(f"{utils.APP_ROOT_DIR}/ai/openai/prompts"))
        self.client = OpenAI()
        self.messages: List[Dict[str, str]] = []

    def get_template_completion(self, template: str, template_params: Dict[str, Any]) -> str:
        template = self.jinja.get_template(template)
        query = template.render(template_params)
        print(f"get_template_completion: {query}")
        message = {"role": "user", "content": query}
        # self.messages.append(message)
        completion = self.client.chat.completions.create(
            model="o1",
            store=False,
            messages=[message]
        )
        completion_text = completion.choices[0].message.content
        # self.messages.append({"role": "assistant", "content": completion_text})
        print(f"completion: {completion_text}")
        return completion_text

    @staticmethod
    def saved_prompt():
        return """
        [{"filename": "react-app/src/App.css", "contents": "body {  margin: 0;  padding: 0;  font-family: sans-serif;}.App {  text-align: center;  margin: 20px;}button {  margin-top: 10px;  padding: 8px 16px;  background-color: #008CBA;  color: #fff;  border: none;  border-radius: 4px;  cursor: pointer;}button:hover {  background-color: #005f73;}"}]
        """

class TestConversation(Conversation):
    def get_template_completion(self, template: str, template_params: Dict[str, str]) -> str:
        return "[]"
