import re
import json
import os
from typing import Dict, List

APP_ROOT_DIR = os.environ['APP_ROOT_DIR']


def extract_all_json_blocks(text) -> list[dict]:
    # Find all JSON code blocks in the text
    try:
        return [json.loads(text)]
    except json.JSONDecodeError as e:
        print(f"Could not decode JSON: {e}")
        pass


    matches = re.findall(r"```json(.*?)```", text, re.DOTALL)
    print(f"Markdown matches {len(matches)}")
    json_blocks = []
    for match in matches:
        try:
            json_blocks.append(json.loads(match.strip()))
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    return json_blocks


def extract_code_blocks_with_filenames(text: str) -> List[Dict[str, str]]:
    """
    Extracts code blocks and their filenames from a Markdown string.

    Args:
        text (str): The input Markdown string.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing filenames and code blocks.
    """
    pattern = r"```(?:([\w./-]+)\s+)?([\s\S]*?)```"
    matches = re.findall(pattern, text)
    code_blocks = []
    for filename, code in matches:
        code_blocks.append({
            "file_path": filename.strip() if filename else "unknown",
            "contents": code.strip()
        })
    return code_blocks


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
