import os
from typing import Optional, Dict, Any
from fastapi import UploadFile
import uuid
from datetime import datetime
import io

from app.core.config import settings

# Optional imports for cloud storage
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("boto3 not available - S3 storage disabled")

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("google-cloud-storage not available - GCS storage disabled")

class StorageService:
    """Storage service for S3/GCS integration"""
    
    def __init__(self):
        self.s3_client = None
        self.gcs_client = None
        self.storage_type = "s3"  # Default to S3
        
        # Initialize storage clients
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage clients based on configuration"""
        try:
            # Initialize S3 if credentials are provided and boto3 is available
            if BOTO3_AVAILABLE and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                print("S3 client initialized successfully")
            
            # Initialize GCS if credentials are provided and google-cloud-storage is available
            if GCS_AVAILABLE and settings.GOOGLE_APPLICATION_CREDENTIALS:
                self.gcs_client = storage.Client()
                print("GCS client initialized successfully")
            
            # Determine primary storage type
            if self.s3_client and self.gcs_client:
                # Both available - use S3 as default
                self.storage_type = "s3"
            elif self.s3_client:
                self.storage_type = "s3"
            elif self.gcs_client:
                self.storage_type = "gcs"
            else:
                print("Warning: No cloud storage configured - using local storage")
                self.storage_type = "local"
                
        except Exception as e:
            print(f"Error initializing storage: {e}")
            self.storage_type = "local"
    
    async def upload_image(self, image_file: UploadFile) -> str:
        """Upload image to cloud storage"""
        try:
            # Generate unique filename
            file_extension = image_file.filename.split('.')[-1] if image_file.filename else 'jpg'
            filename = f"styles/{uuid.uuid4().hex}.{file_extension}"
            
            # Read file content
            content = await image_file.read()
            
            # Upload based on storage type
            if self.storage_type == "s3" and self.s3_client:
                return await self._upload_to_s3(content, filename, image_file.content_type)
            elif self.storage_type == "gcs" and self.gcs_client:
                return await self._upload_to_gcs(content, filename, image_file.content_type)
            else:
                # Fallback to local storage for development
                return await self._upload_to_local(content, filename)
                
        except Exception as e:
            print(f"Error uploading image: {e}")
            raise
    
    async def upload_bytes(self, image_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        """Upload image bytes to cloud storage"""
        try:
            # Generate unique filename if not provided
            if not filename:
                file_extension = "jpg"
                filename = f"styles/{uuid.uuid4().hex}.{file_extension}"
            
            # Upload based on storage type
            if self.storage_type == "s3" and self.s3_client:
                return await self._upload_to_s3(image_bytes, filename, content_type)
            elif self.storage_type == "gcs" and self.gcs_client:
                return await self._upload_to_gcs(image_bytes, filename, content_type)
            else:
                # Fallback to local storage for development
                return await self._upload_to_local(image_bytes, filename)
                
        except Exception as e:
            print(f"Error uploading bytes: {e}")
            raise
    
    async def _upload_to_s3(self, content: bytes, filename: str, content_type: str) -> str:
        """Upload to AWS S3"""
        try:
            self.s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=filename,
                Body=content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            # Return public URL
            url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
            return url
            
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            raise
    
    async def _upload_to_gcs(self, content: bytes, filename: str, content_type: str) -> str:
        """Upload to Google Cloud Storage"""
        try:
            bucket = self.gcs_client.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            
            # Upload content
            blob.upload_from_string(
                content,
                content_type=content_type
            )
            
            # Make public
            blob.make_public()
            
            # Return public URL
            url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{filename}"
            return url
            
        except Exception as e:
            print(f"Error uploading to GCS: {e}")
            raise
    
    async def _upload_to_local(self, content: bytes, filename: str) -> str:
        """Upload to local storage (for development)"""
        try:
            # Create local storage directory
            local_dir = "local_storage"
            os.makedirs(local_dir, exist_ok=True)
            
            # Save file locally
            file_path = os.path.join(local_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Return local file path (in production, this would be a public URL)
            return f"file://{os.path.abspath(file_path)}"
            
        except Exception as e:
            print(f"Error uploading to local storage: {e}")
            raise
    
    async def delete_image(self, image_url: str) -> bool:
        """Delete image from cloud storage"""
        try:
            # Extract filename from URL
            filename = self._extract_filename_from_url(image_url)
            
            if self.storage_type == "s3" and self.s3_client:
                return await self._delete_from_s3(filename)
            elif self.storage_type == "gcs" and self.gcs_client:
                return await self._delete_from_gcs(filename)
            else:
                return await self._delete_from_local(filename)
                
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    async def _delete_from_s3(self, filename: str) -> bool:
        """Delete from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=filename
            )
            return True
        except Exception as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    async def _delete_from_gcs(self, filename: str) -> bool:
        """Delete from GCS"""
        try:
            bucket = self.gcs_client.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting from GCS: {e}")
            return False
    
    async def _delete_from_local(self, filename: str) -> bool:
        """Delete from local storage"""
        try:
            file_path = os.path.join("local_storage", filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting from local storage: {e}")
            return False
    
    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from storage URL"""
        try:
            if url.startswith("https://"):
                # S3 or GCS URL
                parts = url.split("/")
                return "/".join(parts[3:])  # Remove protocol, domain, bucket
            elif url.startswith("file://"):
                # Local file URL
                return url.replace("file://", "").split("local_storage/")[-1]
            else:
                return url
        except Exception:
            return url
    
    async def get_image_metadata(self, image_url: str) -> Dict[str, Any]:
        """Get image metadata from storage"""
        try:
            filename = self._extract_filename_from_url(image_url)
            
            if self.storage_type == "s3" and self.s3_client:
                return await self._get_s3_metadata(filename)
            elif self.storage_type == "gcs" and self.gcs_client:
                return await self._get_gcs_metadata(filename)
            else:
                return await self._get_local_metadata(filename)
                
        except Exception as e:
            print(f"Error getting image metadata: {e}")
            return {}
    
    async def _get_s3_metadata(self, filename: str) -> Dict[str, Any]:
        """Get S3 object metadata"""
        try:
            response = self.s3_client.head_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=filename
            )
            
            return {
                "size": response.get("ContentLength", 0),
                "content_type": response.get("ContentType", ""),
                "last_modified": response.get("LastModified", ""),
                "etag": response.get("ETag", "")
            }
        except Exception as e:
            print(f"Error getting S3 metadata: {e}")
            return {}
    
    async def _get_gcs_metadata(self, filename: str) -> Dict[str, Any]:
        """Get GCS object metadata"""
        try:
            bucket = self.gcs_client.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.reload()
            
            return {
                "size": blob.size,
                "content_type": blob.content_type,
                "last_modified": blob.updated,
                "etag": blob.etag
            }
        except Exception as e:
            print(f"Error getting GCS metadata: {e}")
            return {}
    
    async def _get_local_metadata(self, filename: str) -> Dict[str, Any]:
        """Get local file metadata"""
        try:
            file_path = os.path.join("local_storage", filename)
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    "size": stat.st_size,
                    "content_type": "image/jpeg",  # Default
                    "last_modified": datetime.fromtimestamp(stat.st_mtime),
                    "etag": str(stat.st_mtime)
                }
            return {}
        except Exception as e:
            print(f"Error getting local metadata: {e}")
            return {}
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration information"""
        return {
            "storage_type": self.storage_type,
            "s3_configured": self.s3_client is not None,
            "gcs_configured": self.gcs_client is not None,
            "bucket": settings.AWS_S3_BUCKET if self.storage_type == "s3" else settings.GCS_BUCKET_NAME
        }
