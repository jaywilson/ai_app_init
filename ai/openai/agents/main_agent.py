import json
import uuid
from dataclasses import dataclass
from time import sleep

import openai_utils
import utils
import os
import subprocess


@dataclass
class Command:
    command: list[str]
    wait_for_complete: bool = True
    wait_timout: int = 300


class ProjectAgent:
    OUTPUT_DIR = f"{utils.APP_ROOT_DIR}/generated_projects"

    def __init__(self, openai: openai_utils.OpenAIUtils | None = None):
        self.openai = openai_utils.OpenAIUtils() if openai is None else openai
        self.project_id = uuid.uuid4().hex

    def build_frontend(self, user_requirements: str) -> str:
        template_files = utils.get_template_contents(
            f"{utils.APP_ROOT_DIR}/ai/openai/templates/react/react-app",
            "react-app",
        )
        template_file_paths = list(template_files.keys())
        print(f"Template files {template_file_paths}")

        completion_text = self.openai.get_template_completion(
            "frontend.prompt",
            {
                "user_requirements": user_requirements,
                "template_files": template_file_paths,
            }
        )
        self.write_project(completion_text, template_file_paths, template_files)
        self.run_and_try_fix_commands(
            [
                Command(command=['npm', 'install']),
                Command(command=['npm', 'start'], wait_for_complete=False, wait_timout=10),
            ]
        )
        return completion_text


    def write_project(self, completion_text: str, template_file_paths: list[str], template_files: dict[str, str]):
        completion_files = self.write_completion_files(completion_text)
        for template_file_path in template_file_paths:
            if template_file_path in completion_files:
                continue

            print(f"Completion did not modify {template_file_path}. Using template version.")
            contents = template_files[template_file_path]
            self.write_project_file(template_file_path, contents)
            # azure_utils.upload_json_blob(contents, blob)

    def write_completion_files(self, completion_text: str) -> list[str]:
        completion_file_list = json.loads(completion_text)
        completion_files = []
        for file_obj in completion_file_list:
            file_path = file_obj['filename']
            try:
                contents = file_obj['contents']
                self.write_project_file(file_path, contents)
                completion_files.append(file_path)
            except Exception as e:
                print(f"Error: {str(e)} File: {file_path}")
        return completion_files

    def write_project_file(self, file_path: str, contents: str):
        project_path = f"{self.project_id}/{file_path}"
        output_path = os.path.join(ProjectAgent.OUTPUT_DIR, project_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            print(f"Writing: {output_path}")
            f.write(contents)

    def run_and_try_fix_commands(self, commands: list[Command]):
        max_tries = 3
        cur_try = 0
        success = False
        while not success and cur_try < max_tries:
            cur_try += 1
            for command in commands:
                success = self.run_command(command)

    def run_command(self, command: Command) -> bool:
        print(f"running {command}")
        project_path = os.path.join(ProjectAgent.OUTPUT_DIR, self.project_id, 'react-app')
        process = subprocess.Popen(
            command.command,
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL
        )
        if command.wait_for_complete:
            process.wait(command.wait_timout)
        else:
            sleep(command.wait_timout)

        # Check if the command was successful
        if process.poll() is not None and process.returncode != 0:
            stdout, stderr = process.communicate()
            print(f"{command} failed with return code {process.returncode}")
            output = f"stdout: {stdout.decode()[0:500]} stderr: {stderr.decode()[0:500]}"
            print(f"stdout: {output}")
            self.fix_command_error(command.command, output)
            return False
        else:
            print(f"{command} success")
            return True

    def fix_command_error(self, command: list[str], error: str):
        error_completion = self.openai.get_template_completion("frontend_error.prompt", {
            "command": " ".join(command),
            "error": error,
        })
        print(f"Error completion: {error_completion}")
        self.write_completion_files(error_completion)
