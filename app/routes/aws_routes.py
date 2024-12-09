import boto3
from app.config import BUCKET_NAME, S3_LOCATION, S3_KEY, S3_SECRET

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)


def upload_file_to_s3(file, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # in case the s3 upload fails
        return {'errors': str(e)}

    return {'url': f'{S3_LOCATION}/{file.filename}'}


def remove_file_from_s3(file_url):
    # AWS needs the image file name, not the URL
    key = file_url.rsplit("/", 1)[1]
    print(key)
    try:
        s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=key
        )
    except Exception as e:
        return {'errors': str(e) }
    return True
