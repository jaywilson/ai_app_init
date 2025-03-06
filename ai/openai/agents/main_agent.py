import uuid
import openai_utils
import utils
import azure_utils

class MainAgent:
    @staticmethod
    def build_frontend(user_requirements: str) -> str:
        temp_root = uuid.uuid4().hex
        template_files = utils.read_templates_and_output_to_temp(
            "/home/kiz/app/ai/openai/templates/react/react-app",
            "react-app",
            temp_root
        )

        print(f"template files {template_files}")
        openai = openai_utils.OpenAIUtils()
        completion_text = openai.get_template_completion(
            "frontend.prompt",
            {
                "user_requirements": user_requirements,
                "template_files": template_files,
            }
        )

        blob_dir = uuid.uuid4().hex
        print(f"uploading to {blob_dir}")
        for file_list in utils.extract_all_json_blocks(completion_text):
            for f in file_list:
                try:
                    filename = f['filename']
                    contents = f['contents']
                    blob = f"{blob_dir}/{filename}"
                    print(f"Uploading: {contents} {blob}")
                    azure_utils.upload_json_blob(contents, blob)
                except Exception as e:
                    print(f"Error: {str(e)} File: {f}")

        return completion_text
