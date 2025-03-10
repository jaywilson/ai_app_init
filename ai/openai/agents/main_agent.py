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

    def __init__(self, conversation: openai_utils.Conversation | None = None):
        self.project_id = uuid.uuid4().hex
        self.project_path = ProjectAgent.get_project_path(self.project_id)
        self.project_zip_path = ProjectAgent.get_project_zip_path(self.project_id)
        self.react_app_path = os.path.join(self.project_path, 'react-app')
        self.server_path = os.path.join(self.project_path, 'server')
        self.azure = azure_utils.Azure()
        self.conversation = conversation if conversation is not None else openai_utils.Conversation()

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

        requirements_completion = json.loads(self.conversation.get_template_completion(
            "requirements.prompt",
            {
                "user_requirements": user_requirements,
            }
        ))
        requirements = requirements_completion['requirements']
        server_api = requirements_completion['server_api']

        frontend_completion = self.conversation.get_template_completion(
            "frontend.prompt",
            {
                "requirements": requirements,
                "server_api": server_api,
                "template_files": template_file_paths,
            }
        )

        self.write_project(frontend_completion, template_file_paths, template_files)
        error = self.run_and_try_fix_commands(
            self.react_app_path,
            [
                Command(command=['npm', 'install']),
                Command(command=['npm', 'start'], wait_for_complete=False, wait_timout=10, kill=True),
            ]
        )

        backend_completion = self.conversation.get_template_completion(
            "backend.prompt",
            {
                "server_api": server_api,
            }
        )
        print(f"Backend completion: {backend_completion}")
        self.write_project(backend_completion, [], {})
        error = self.run_and_try_fix_commands(
            self.server_path,
            [
                Command(command=['gradle', 'build']),
            ]
        )

        self.upload()
        # self.delete()
        # testing so don't delete
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

    def run_and_try_fix_commands(self, working_dir: str, commands: list[Command]) -> str | None:
        max_tries = 3
        cur_try = 0
        error = ""
        while error is not None and cur_try < max_tries:
            cur_try += 1
            for command in commands:
                error = self.run_command(working_dir, command)
        return error

    def run_command(self, working_dir: str, command: Command) -> str | None:
        print(f"running {command}")
        process = subprocess.Popen(
            command.command,
            cwd=working_dir,
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
            self.fix_command_error(working_dir, command.command, output)
            return output
        else:
            print(f"{command} success")
            if command.kill:
                process.kill()
                print(f"{command} killed successfully")
            return None

    def fix_command_error(self, working_dir: str, command: list[str], error: str):
        error_completion = self.conversation.get_template_completion("fix_error.prompt", {
            "working_dir": working_dir,
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
