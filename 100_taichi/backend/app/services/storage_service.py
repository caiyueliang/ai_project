import os
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from typing import Optional
from ..database import settings

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False  # 设为True如果使用HTTPS
        )
        self.bucket_name = settings.minio_bucket
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")
    
    def upload_audio(self, file_data: bytes, file_name: str, user_id: str) -> Optional[str]:
        """上传音频文件到对象存储"""
        try:
            object_name = f"audio/{user_id}/{datetime.now().strftime('%Y%m%d')}/{file_name}"
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                len(file_data),
                content_type="audio/mpeg"
            )
            return f"http://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            print(f"Error uploading audio: {e}")
            return None
    
    def upload_video(self, file_data: bytes, file_name: str, user_id: str) -> Optional[str]:
        """上传视频文件到对象存储"""
        try:
            object_name = f"video/{user_id}/{datetime.now().strftime('%Y%m%d')}/{file_name}"
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                len(file_data),
                content_type="video/mp4"
            )
            return f"http://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            print(f"Error uploading video: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """删除存储的文件"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """生成预签名URL用于临时访问"""
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None