import re
import json
import os
from typing import Dict


def extract_all_json_blocks(text):
    # Find all JSON code blocks in the text
    matches = re.findall(r"```json\s*([\s\S]*?)```", text)
    json_blocks = []
    for match in matches:
        try:
            json_blocks.append(json.loads(match.strip()))
        except json.JSONDecodeError as e:
           print("Error decoding JSON:", e)
    return json_blocks


def get_template_contents(template_dir: str, template_name: str) -> Dict[str, str]:
    file_contents = {}
    for root, _, files in os.walk(template_dir):
        for file in files:
            if "node_modules" in root:
                continue

            try:
                source_file_path = os.path.join(root, file)
                s = source_file_path.find(template_name)
                relpath = source_file_path[s:]
                with open(source_file_path, 'r') as src_file:
                    file_contents[relpath] = src_file.read()
            except Exception as e:
                print(f"Error reading file {file}: {str(e)}")

    return file_contents
