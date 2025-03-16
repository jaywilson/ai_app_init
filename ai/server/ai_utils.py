from typing import Dict, List, Any

from openai import OpenAI
import anthropic
import jinja2
import utils


class Conversation:
    def __init__(self):
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(f"{utils.APP_ROOT_DIR}/ai/server/prompts"))
        self.openai_client = OpenAI()
        self.claude_client = anthropic.Anthropic()
        self.messages: List[Dict[str, str]] = []

    def get_template_completion(self, template: str, template_params: Dict[str, Any]) -> str:
        template = self.jinja.get_template(template)
        query = template.render(template_params)
        print(f"get_template_completion: {query}")
        message = {"role": "user", "content": query}
        # self.messages.append(message)
        message = self.claude_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8192,
            messages=[message]
        )
        text = message.content[0].text
        # self.messages.append({"role": "assistant", "content": completion_text})
        print(f"completion: {text}")
        return text

    @staticmethod
    def saved_prompt():
        return """
        [{"filename": "react-app/src/App.css", "contents": "body {  margin: 0;  padding: 0;  font-family: sans-serif;}.App {  text-align: center;  margin: 20px;}button {  margin-top: 10px;  padding: 8px 16px;  background-color: #008CBA;  color: #fff;  border: none;  border-radius: 4px;  cursor: pointer;}button:hover {  background-color: #005f73;}"}]
        """

class TestConversation(Conversation):
    def get_template_completion(self, template: str, template_params: Dict[str, str]) -> str:
        return "[]"
