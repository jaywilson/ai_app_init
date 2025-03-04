import os
import json

def get_react_app() -> dict:
    base_dir = "/home/kiz/app/ai/app_init/react/react-app"
    dir_contents = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                if "node_modules" in file_path \
                    or ".png" in file_path \
                    or ".ico" in file_path \
                    or ".svg" in file_path \
                    or "package-lock" in file_path \
                    or "README.md" in file_path \
                    or "gitignore" in file_path:
                    continue
                print(f"File: {file_path}")
                content = f.read()
            # Create dictionary with filename and contents
            dir_contents.append({
                "filename": os.path.relpath(file_path, base_dir),
                "contents": content
            })
    return dir_contents