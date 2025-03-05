import os
import uuid

def read_templates_and_output_to_temp(templates_dir: str, template_name) -> str | None:
    temp_root = None
    try:
        temp_root = uuid.uuid4().hex
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if "node_modules" in root:
                    continue

                source_file_path = os.path.join(root, file)
                s = source_file_path.find(template_name)
                relpath = source_file_path[s:]
                dest_file_path = os.path.join("/home/kiz/app/gencode", temp_root, relpath)
                print(f"Copying file to {dest_file_path}")

                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                with open(source_file_path, 'r') as src_file, open(dest_file_path, 'w') as dest_file:
                    dest_file.write(src_file.read())
                    pass

        print(f"File contents copied to: {temp_root}")
    except Exception as e:
        print(f"Error copying files: {str(e)}")
    return temp_root


