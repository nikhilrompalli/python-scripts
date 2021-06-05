import boto3

_BUCKET_NAME = 'builds'
_PREFIX = ''

client = boto3.client('s3', aws_access_key_id="",
                            aws_secret_access_key="")

def ListFiles(client):
    """List files in specific S3 URL"""
    response = client.list_objects(Bucket=_BUCKET_NAME, Prefix=_PREFIX)
    for content in response.get('Contents', []):
        yield content.get('Key')

file_list = ListFiles(client)
for file in file_list:
    print 'File found: %s' % file