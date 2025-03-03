import asyncio

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def upload_json_blob(contents: str):
    # Acquire a credential object
    token_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
            account_url="https://kizarastore.blob.core.windows.net",
            credential=token_credential)
    blob_client = blob_service_client.get_blob_client(container="app", blob="test_blob")
    blob_client.upload_blob(contents)

upload_json_blob('{"test": "test"}')
