import re
import json

def extract_all_json_blocks(text):
    try:
        # Find all JSON code blocks in the text
        matches = re.findall(r"```json\s*([\s\S]*?)```", text)
        json_blocks = []
        for match in matches:
            json_blocks.append(json.loads(match.strip()))
        return json_blocks
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return []