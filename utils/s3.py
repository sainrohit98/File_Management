import boto3
from file_manager import AWS_BUCKET_NAME
from django.shortcuts import HttpResponse

def upload_file_to_s3(file, s3_key):
    """
    Uploads a file to S3.

    Args:
        file: The file object to upload.
        s3_key: The key under which to store the file in S3.

    Returns:
        None
    """
    s3_client = boto3.client('s3')

    # Upload the file to S3
    s3_client.upload_fileobj(file, AWS_BUCKET_NAME, s3_key)


def rename_file_in_s3(old_s3_key, new_s3_key):
    """
    Renames a file in S3.

    Args:
        old_s3_key: The current key of the file to be renamed.
        new_s3_key: The new key to rename the file.

    Returns:
        None
    """
    s3_client = boto3.client('s3')

    # Copy the file to a new key
    s3_client.copy_object(
        Bucket=AWS_BUCKET_NAME,
        CopySource={'Bucket': AWS_BUCKET_NAME, 'Key': old_s3_key},
        Key=new_s3_key
    )

    # Delete the old file
    delete_file_from_s3(old_s3_key)


def delete_file_from_s3(s3_key):
    """
    Deletes a file from S3.

    Args:
        s3_key: The key of the file to be deleted.

    Returns:
        None
    """
    s3_client = boto3.client('s3')

    # Delete the file from S3
    s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)



def get_file(s3_key):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='demo-file-management', Key=s3_key)
    file_content = response['Body'].read()

    # Set the content disposition to force download
    response = HttpResponse(file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{s3_key.split("/")[-1]}"'
    return response

