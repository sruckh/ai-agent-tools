
import os
import uuid
from typing import Dict, Any

from loguru import logger

from runpod_base import RunPodBaseHandler, RunPodStorageHandler, create_temp_directory, cleanup_temp_directory, extract_file_from_base64


class RunPodStorageManagerHandler(RunPodBaseHandler):
    def __init__(self):
        super().__init__()
        self.storage = RunPodStorageHandler()

    def process_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        input_data = self.validate_input(event)
        operation = input_data["operation"]
        parameters = input_data.get("parameters", {})

        if operation == "upload":
            return self._upload(parameters)
        elif operation == "download":
            return self._download(parameters)
        elif operation == "delete":
            return self._delete(parameters)
        elif operation == "status":
            return self._status(parameters)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _upload(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        media_type = parameters.get("media_type")
        if not media_type:
            raise ValueError("Missing required parameter: media_type")

        s3_key = f"{media_type}/{uuid.uuid4().hex}"
        
        if "file_data" in parameters:
            temp_dir = create_temp_directory()
            try:
                local_path = os.path.join(temp_dir, "upload_file")
                extract_file_from_base64(parameters["file_data"], local_path)
                file_url = self.storage.upload_file(local_path, s3_key)
            finally:
                cleanup_temp_directory(temp_dir)
        elif "url" in parameters:
            file_url = self.storage.upload_from_url(parameters["url"], s3_key)
        else:
            raise ValueError("Missing required parameter: file_data or url")

        download_url = self.storage.generate_presigned_url(s3_key)

        result = {
            "file_id": s3_key,
            "file_url": file_url,
            "download_url": download_url,
        }
        return self.create_success_response(result)

    def _download(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        file_id = parameters.get("file_id")
        if not file_id:
            raise ValueError("Missing required parameter: file_id")

        download_url = self.storage.generate_presigned_url(file_id)
        
        result = {
            "file_id": file_id,
            "download_url": download_url,
        }
        return self.create_success_response(result)

    def _delete(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        file_id = parameters.get("file_id")
        if not file_id:
            raise ValueError("Missing required parameter: file_id")

        self.storage.s3_client.delete_object(Bucket=self.storage.bucket_name, Key=file_id)
        
        return self.create_success_response({"status": "success"})

    def _status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        file_id = parameters.get("file_id")
        if not file_id:
            raise ValueError("Missing required parameter: file_id")

        try:
            self.storage.s3_client.head_object(Bucket=self.storage.bucket_name, Key=file_id)
            status = "ready"
        except Exception:
            status = "not_found"
            
        return self.create_success_response({"status": status})

def handler(event):
    storage_handler = RunPodStorageManagerHandler()
    return storage_handler.handler(event)

if __name__ == "__main__":
    # This is for local testing
    pass
