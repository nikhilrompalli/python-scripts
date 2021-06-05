'''
# Install boto3 using "pip install boto3" if not available
'''
import sys, json, glob
import boto3
import boto3
from botocore.client import Config
from boto3.s3.transfer import S3Transfer

aws_access_key    = ""
aws_access_secret = ""

if len(sys.argv) < 2:
    print ("Please provide file path.")
    print ("Ex: python upload-to-s3.py /data/jenkins/workspace/project/content_list.json")
    sys.exit()
    
def push_s3(env , file):
    try:
        bucket_name = 'builds'
        ''' Upload file '''
        client      = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_access_secret, config=Config(signature_version='s3v4'))
        transfer    = S3Transfer(client)
    
        if file:
            print ("Uploading %s..." % (file))
            transfer.upload_file(file, bucket_name , env + "/" + file.split('/')[-1], extra_args={'ACL': 'public-read'})
            print ("Uploaded")
        else:
            print ("No files found for upload.")
    except Exception, err:
        print "Unexpected Exception at push_s3 : " + str(err)
        
try:
    file = sys.argv[2]
    env = sys.argv[1]
    
    bucket_name = ''
    push_s3(env, file)

except Exception as e:
    print ("Exception: " + str(e))
    sys.exit()
