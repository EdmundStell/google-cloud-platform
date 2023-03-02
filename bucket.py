import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./my-key.json"

from google.cloud import storage
from google.api_core.exceptions import Conflict, BadRequest

client = storage.Client()

buckets = [bucket.name for bucket in client.list_buckets()]

print(f'\nBuckets: {buckets}\n')

class Bucket():
    client = storage.Client()

    # print([a for a in dir(client.bucket('name')) if not a.startswith('_')])

    def __init__(self, bucket):
        self.bucket = Bucket.client.bucket(bucket)

        if self.bucket.name in [bucket.name for bucket in Bucket.client.list_buckets()]:
            print(f'Using {bucket} which already exists in your project\n')
        else:
            try:
                self.bucket.create()
            except BadRequest as e:
                if 'Bucket names must be at least 3 characters in length' in str(e):
                    raise ValueError(f'Error: Bucket name "{bucket}" must be at least 3 characters in length')
                else:
                    raise(e)
            except Conflict:
                raise ValueError(f'Bucket {bucket} already exists globally')

            print(f'Bucket {bucket} created\n')

    def list_files(self):
        blobs = self.bucket.list_blobs()
        l = [blob.name for blob in blobs]
        print(f'files: {l}\n')
        return l

    def upload_file(self, file_name, file_path):
        blob = self.bucket.blob(file_name)  
        blob.upload_from_filename(file_path)
        print(f'{file_name} uploaded\n')
        return file_name

    def download_file(self, file_name):
        blob = self.bucket.blob(file_name)
        blob.download_to_filename(f'./{file_name}')
        print(f'{file_name} downloaded\n')
    
    def read_text_file(self, file_name):
        blob = self.bucket.blob(file_name)
        contents = blob.download_as_string().decode('utf-8')
        print(f'{contents}\n')
        return contents
    
    def rename_blob(self, file_name, new_file_name):
        blob = self.bucket.blob(file_name)
        self.bucket.rename_blob(blob, new_file_name)
        print(f'{file_name} renamed to {new_file_name}\n')
    
    def delete_file(self, file_name):
        blob = self.bucket.blob(file_name)
        blob.delete()
        print(f'{file_name} deleted!\n')

    def empty_bucket(self):
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            blob.delete()
        print(f"All blobs in {self.bucket.name} bucket deleted.\n")
    
    def self_destruct(self):
        self.bucket.delete(force=True)
        print(f'KABOOM! Bucket {self.bucket.name} and all contents deleted\n')

bucket = 'edmund-test-bucket'
file = 'zen.txt'
file_path = './zen_of_python.txt'

def master():
    try:
        os.remove('zen.txt')
    except OSError:
        pass

    test_bucket = Bucket(bucket)
    test_bucket.list_files()
    test_bucket.upload_file(file, file_path)
    test_bucket.list_files()
    test_bucket.download_file(file)
    test_bucket.read_text_file(file)
    # test_bucket.rename_blob(file, 'zen1.txt')
    test_bucket.delete_file(file)
    test_bucket.list_files()
    test_bucket.self_destruct()

if __name__ == '__main__':
    master()
