from azure.storage.blob import BlobServiceClient
import shutil
import os

class Storage:
    def __init__(self, connection_string, base_path=''):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.base_path = base_path.rstrip('/')

    def _get_container_and_blob_names(self, path):
        full_path = f"{self.base_path}/{path}".lstrip('/')
        path_parts = full_path.split('/')
        container_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])
        return container_name, blob_name

    def mkdir(self, path):
        container_name, _ = self._get_container_and_blob_names(path)
        if not self.blob_service_client.get_container_client(container_name).exists():
            self.blob_service_client.create_container(container_name)

    def listdir(self, path):
        container_name, blob_name = self._get_container_and_blob_names(path)
        container_client = self.blob_service_client.get_container_client(container_name)
        items = []
        for blob in container_client.list_blobs(name_starts_with=blob_name):
            item = blob.name[len(blob_name):]
            if item.startswith('/'):
                item = item.lstrip('/')
                if '/' in item:
                    item = item.split('/', 1)[0] + '/'
                if item and item not in items:
                    items.append(item.rstrip('/'))
        return items
    
    def path_join(self, *args):
        return '/'.join(args)

    def exists(self, path):
        container_name, blob_name = self._get_container_and_blob_names(path)
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            return False
        if not blob_name:
            return True
        for blob in container_client.list_blobs(name_starts_with=blob_name):
            if blob.name == blob_name or blob.name.startswith(f"{blob_name}/"):
                return True
        return False

    def read_file(self, path, mode='t'):
        container_name, blob_name = self._get_container_and_blob_names(path)
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        data = blob_client.download_blob().readall()
        if mode == 't':
            return data.decode('utf-8')
        else:
            return data

    def write_file(self, path, data):
        container_name, blob_name = self._get_container_and_blob_names(path)
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)

class FS_Storage:
    def __init__(self, base_path=''):
        self.base_path = base_path.rstrip('/')

    def _get_full_path(self, path):
        return os.path.join(self.base_path, path)

    def mkdir(self, path):
        full_path = self._get_full_path(path)
        os.makedirs(full_path, exist_ok=True)

    def listdir(self, path):
        full_path = self._get_full_path(path)
        return os.listdir(full_path)
    
    def path_join(self, *args):
        return os.path.join(*args)

    def exists(self, path):
        full_path = self._get_full_path(path)
        return os.path.exists(full_path)
    
    def delete(self, path):
        full_path = self._get_full_path(path)
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            raise ValueError(f"'{path}' is not a file or directory")

    def read_file(self, path, mode='t'):
        full_path = self._get_full_path(path)
        with open(full_path, f'r{mode}') as f:
            return f.read()

    def write_file(self, path, data):
        full_path = self._get_full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        mode = 'w' if isinstance(data, str) else 'wb'
        with open(full_path, mode) as f:
            f.write(data)