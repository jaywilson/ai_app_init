import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

class Azure:
    def __init__(self):
        self.token_credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(
            account_url="https://kizarastore.blob.core.windows.net",
            credential=self.token_credential)
        self.container_client = self.blob_service_client.get_container_client("app")

    def upload_json_blob(self, contents: str, blob: str):
        blob_client = self.blob_service_client.get_blob_client(container="app", blob=blob)
        blob_client.upload_blob(contents)

    def upload_file(self, source: str, dest: str):
        '''
        Upload a single file to a path inside the container
        '''
        print(f'Uploading {source} to {dest}')
        with open(source, 'rb') as data:
            self.container_client.upload_blob(name=dest, data=data)

    def upload_dir(self, source: str):
        '''
        Upload a directory to a path inside the container
        '''
        count = 0
        max_count = 100
        prefix = os.path.basename(source) + '/'
        for root, dirs, files in os.walk(source):
            for name in files:
                file_path = os.path.join(root, name)
                if self.is_file_filtered(file_path):
                    continue

                dir_part = os.path.relpath(root, source)
                dir_part = '' if dir_part == '.' else dir_part + '/'
                blob_path = prefix + dir_part + name
                self.upload_file(file_path, blob_path)
                count += 1
                if count > max_count:
                    break
            if count > max_count:
                break
        print(f"Azure: Uploaded {count} files from {source}")

    @staticmethod
    def is_file_filtered(file_path: str):
        return "node_modules" in file_path
