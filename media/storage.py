from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
import boto3
from botocore.exceptions import ClientError

class CloudflareR2Storage(Storage):
    def __init__(self):
        self.access_key = settings.CLOUDFLARE_R2_ACCESS_KEY_ID
        self.secret_key = settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME
        self.endpoint_url = settings.CLOUDFLARE_R2_ENDPOINT_URL
        self.custom_domain = settings.CLOUDFLARE_R2_CUSTOM_DOMAIN
        
        if self.access_key and self.secret_key and self.bucket_name and self.endpoint_url:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            )
        else:
            self.client = None

    def _save(self, name, content):
        if not self.client:
            raise ValueError("Cloudflare R2 credentials not configured")
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=name,
                Body=content.read(),
                ContentType=content.content_type if hasattr(content, 'content_type') else 'application/octet-stream'
            )
            return name
        except ClientError as e:
            raise Exception(f"Failed to upload to R2: {str(e)}")

    def _open(self, name, mode='rb'):
        if not self.client:
            raise ValueError("Cloudflare R2 credentials not configured")
        
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=name)
            return ContentFile(response['Body'].read())
        except ClientError as e:
            raise Exception(f"Failed to download from R2: {str(e)}")

    def delete(self, name):
        if not self.client:
            raise ValueError("Cloudflare R2 credentials not configured")
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=name)
        except ClientError as e:
            raise Exception(f"Failed to delete from R2: {str(e)}")

    def exists(self, name):
        if not self.client:
            return False
        
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except ClientError:
            return False

    def url(self, name):
        if self.custom_domain:
            return f"{self.custom_domain}/{name}"
        return f"{self.endpoint_url}/{self.bucket_name}/{name}"

    def size(self, name):
        if not self.client:
            raise ValueError("Cloudflare R2 credentials not configured")
        
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=name)
            return response['ContentLength']
        except ClientError as e:
            raise Exception(f"Failed to get file size from R2: {str(e)}")

