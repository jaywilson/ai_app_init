import re
import json

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
