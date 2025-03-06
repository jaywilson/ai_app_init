import re
import json
import os
from typing import List


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

def read_templates_and_output_to_temp(template_dir: str, template_name, temp_root) -> List[str]:
    rel_paths = []
    try:
        for root, _, files in os.walk(template_dir):
            for file in files:
                if "node_modules" in root:
                    continue

                source_file_path = os.path.join(root, file)
                s = source_file_path.find(template_name)
                relpath = source_file_path[s:]
                rel_paths.append(relpath)
                dest_file_path = os.path.join("/home/kiz/app/gencode", temp_root, relpath)
                print(f"Copying file to {dest_file_path}")

                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                with open(source_file_path, 'r') as src_file, open(dest_file_path, 'w') as dest_file:
                    # dest_file.write(src_file.read())
                    pass

        print(f"File contents copied to: {temp_root}")
    except Exception as e:
        print(f"Error copying files: {str(e)}")

    return rel_paths


