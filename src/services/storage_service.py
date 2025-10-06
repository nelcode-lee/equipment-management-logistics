"""
Service for handling image storage and file management
"""
import boto3
import uuid
from typing import Optional
from ..config import settings

class StorageService:
    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        else:
            self.s3_client = None
    
    def upload_image(self, image_bytes: bytes, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload image to S3 and return the URL
        """
        if not self.s3_client:
            return None
        
        try:
            # Generate unique filename
            filename = f"delivery_notes/{uuid.uuid4()}.jpg"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=filename,
                Body=image_bytes,
                ContentType=content_type
            )
            
            # Return S3 URL
            return f"s3://{settings.S3_BUCKET_NAME}/{filename}"
            
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return None
    
    def get_image_url(self, s3_key: str) -> str:
        """
        Generate a presigned URL for accessing the image
        """
        if not self.s3_client:
            return s3_key
        
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=3600  # 1 hour
            )
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return s3_key

# Global instance
storage_service = StorageService()

