import uuid

import boto3
from django.conf import settings


class StorageService:
    def read(self, path):
        raise NotImplementedError("Read functionality not implemented")

    def write(self, path, file):
        raise NotImplementedError("Write functionality not implemented")


class AWSStorage(StorageService):
    def __init__(self, bucket=None):
        self.storage = boto3.resource(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        self.bucket_name = bucket if bucket else settings.AWS_S3_BUCKET_NAME
        self.bucket = self.storage.Bucket(self.bucket_name)

    def get_file_name(self, file, name=None):
        if not file:
            raise Exception("'file' was not found")
        if name:
            return name

        file_format = file.name.split(".")
        if len(file_format) <= 1:
            raise Exception("Unable to define file extension")
        return "{}.{}".format(str(uuid.uuid1()), file_format[-1])

    def _handle_path(self, path):
        if not path.startswith("/") and path.endswith("/"):
            return path
        raise Exception("Valid 'path' format 'root/path_1/.../path_n/'")

    def write(self, path, file, name=None, access="authenticated-read"):
        key = "{}{}{}".format(
            settings.CDN_FOLDER_PREFIX, self._handle_path(path), self.get_file_name(file, name)
        )
        return self.bucket.put_object(
            Key=key,
            Body=file,
            ACL=access,
            ContentType=getattr(file, "content_type", ""),
        )

    @staticmethod
    def get_signed_url(bucket, key, expiration=3600):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        response = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expiration
        )
        return response

    @staticmethod
    def get_object(bucket, key):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return obj

    @staticmethod
    def delete_object(bucket, key):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        obj = s3_client.delete_object(Bucket=bucket, Key=key)
        return obj
