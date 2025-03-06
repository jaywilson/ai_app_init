from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def upload_json_blob(contents: str, blob: str):
    # Acquire a credential object
    token_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
            account_url="https://kizarastore.blob.core.windows.net",
            credential=token_credential)
    blob_client = blob_service_client.get_blob_client(container="app", blob=blob)
    blob_client.upload_blob(contents)
