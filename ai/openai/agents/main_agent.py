import json
import uuid
from dataclasses import dataclass
from time import sleep

import openai_utils
import utils
import os
import shutil
import subprocess
import azure_utils
import zipfile


@dataclass
class Command:
    command: list[str]
    wait_for_complete: bool = True
    wait_timout: int = 300
    kill: bool = False

@dataclass
class Project:
    project_id: str | None
    error: str | None


class ProjectAgent:
    OUTPUT_DIR = f"{utils.APP_ROOT_DIR}/generated_projects"

    def __init__(self, openai: openai_utils.OpenAIUtils | None = None):
        self.project_id = uuid.uuid4().hex
        self.project_path = ProjectAgent.get_project_path(self.project_id)
        self.project_zip_path = ProjectAgent.get_project_zip_path(self.project_id)
        self.react_app_path = os.path.join(self.project_path, 'react-app')
        self.openai = openai_utils.OpenAIUtils() if openai is None else openai
        self.azure = azure_utils.Azure()

    @staticmethod
    def get_project_path(project_id: str):
        return os.path.join(ProjectAgent.OUTPUT_DIR, project_id)

    @staticmethod
    def get_project_zip_path(project_id: str):
        return os.path.join(ProjectAgent.get_project_path(project_id), "project.zip")

    def build_frontend(self, user_requirements: str) -> Project:
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
        error = self.run_and_try_fix_commands(
            [
                Command(command=['npm', 'install']),
                Command(command=['npm', 'start'], wait_for_complete=False, wait_timout=10, kill=True),
            ]
        )
        self.upload()
        self.delete()
        return Project(self.project_id, error)


    def write_project(self, completion_text: str, template_file_paths: list[str], template_files: dict[str, str]):
        # Create project directory structure
        completion_files = self.write_completion_files(completion_text)
        for template_file_path in template_file_paths:
            if template_file_path in completion_files:
                continue

            print(f"Completion did not modify {template_file_path}. Using template version.")
            contents = template_files[template_file_path]
            self.write_project_file(template_file_path, contents)

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
        output_path = os.path.join(self.project_path, file_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            print(f"Writing: {output_path}")
            f.write(contents)

    def run_and_try_fix_commands(self, commands: list[Command]) -> str | None:
        max_tries = 3
        cur_try = 0
        error = ""
        while error is not None and cur_try < max_tries:
            cur_try += 1
            for command in commands:
                error = self.run_command(command)
        return error

    def run_command(self, command: Command) -> str | None:
        print(f"running {command}")
        process = subprocess.Popen(
            command.command,
            cwd=self.react_app_path,
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
            return output
        else:
            print(f"{command} success")
            if command.kill:
                process.kill()
                print(f"{command} killed successfully")
            return None

    def fix_command_error(self, command: list[str], error: str):
        error_completion = self.openai.get_template_completion("frontend_error.prompt", {
            "command": " ".join(command),
            "error": error,
        })
        print(f"Error completion: {error_completion}")
        self.write_completion_files(error_completion)

    def upload(self):
        # todo azure TTL
        count = 0
        max_count = 100
        is_max_count = False
        with zipfile.ZipFile(self.project_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_path):
                if count > max_count:
                    is_max_count = True
                    break

                for file in files:
                    file_path = os.path.join(root, file)
                    if "node_modules" in file_path:
                        continue

                    arcname = os.path.relpath(file_path, self.project_path)
                    zipf.write(file_path, arcname)
                    count += 1
                    if count > max_count:
                        break

        if is_max_count:
            print(f"Warning: Uploading max count files ({max_count}).")
        else:
            print(f"Uploading {count} files.")

        with open(self.project_zip_path, 'rb') as f:
            contents = f.read()
            upload_path = f"{self.project_id}/project.zip"
            self.azure.upload_blob(contents, upload_path)
            print(f"Uploaded project zip {self.project_zip_path}")

    def delete(self):
        shutil.rmtree(self.project_path)
        print(f"Deleted project {self.project_path}")
