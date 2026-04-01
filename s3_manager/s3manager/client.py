import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path
import os

class s3Manager:
    def __init__(self, profile_name=None, region_name="us-east-1"):
        try:
            session = boto3.Session(profile_name=profile_name, region_name=region_name)
            self.s3 = session.client("s3")
            self.region = region_name
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found. Run `aws configure` first.")

    def list_buckets(self):
        response = self.s3.list_buckets()
        names = []
        for b in response.get("Buckets",[]):
            names.append(b["Name"])
        return names
    
    def create_buckets(self,bucket_name):
        try:
            if self.region == "us-east-1":
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )
            print(f"✅ Bucket '{bucket_name}' created.")
        
        except ClientError as e:
            raise RuntimeError(f"Could not create bucket: {e.response['Error']['Message']}")

    def list_objects(self, bucket_name, prefix=""):
        paginator = self.s3.get_paginator("list_objects_v2")
        objects = []
        for page in paginator.paginate(Bucket = bucket_name, prefix=prefix):
            for obj in page.get("Contents", []):
                objects.append({
                    "key": obj["key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M"),
                })
        return objects

    def upload_file(self, local_path, bucket_name, s3_key=None):
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        s3_key = s3_key or local_path.name
        file_size = local_path.stat().st_size
        
        print(f"⬆️  Uploading '{local_path.name}' ({self._human_size(file_size)}) → s3://{bucket_name}/{s3_key}")
        try:
            self.s3.upload_file(
                str(local_path),
                bucket_name,
                s3_key,
                Callback = ProgressCallback(file_size)
            )
            print(f"\n✅ Upload complete.")
        except ClientError as e:
            raise RuntimeError(f"Upload failed: {e.response['Error']['Message']}") 
            
    def download_file(self, bucket_name, s3_key, local_path=None):
        local_path = Path(local_path or Path(s3_key).name)
        try:
            meta = self.s3.head_object(Bucket=bucket_name, Key=s3_key)
            file_size = meta["ContentLength"]
        except ClientError as e:
            raise RuntimeError(f"Object not found: {e.response['Error']['Message']}")
        print(f"⬇️  Downloading s3://{bucket_name}/{s3_key} ({self._human_size(file_size)}) → '{local_path}'")
        self.s3.download_file(
            bucket_name,
            s3_key,
            str(local_path),
            Callback=ProgressCallback(file_size),
        )
        print(f"\n✅ Download complete.")
       
    def delete_object(self, bucket_name, s3_key):
        """Delete a single object from S3."""
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=s3_key)
            print(f"🗑️  Deleted s3://{bucket_name}/{s3_key}")
        except ClientError as e:
            raise RuntimeError(f"Delete failed: {e.response['Error']['Message']}")
    
    def presigned_url(self, bucket_name, s3_key, expiry=3600):
        """Generate a presigned URL for an object (default 1 hour)."""
        try:
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": s3_key},
                ExpiresIn=expiry,
            )
            return url
        except ClientError as e:
            raise RuntimeError(f"Could not generate URL: {e.response['Error']['Message']}")           
        
    def copy_object(self, src_bucket, src_key, dst_bucket, dst_key=None):
        """Copy an object within or across buckets."""
        dst_key = dst_key or src_key
        try:
            self.s3.copy_object(
                CopySource={"Bucket": src_bucket, "Key": src_key},
                Bucket=dst_bucket,
                Key=dst_key,
            )
            print(f"📋 Copied s3://{src_bucket}/{src_key} → s3://{dst_bucket}/{dst_key}")
        except ClientError as e:
            raise RuntimeError(f"Copy failed: {e.response['Error']['Message']}")
            
    @staticmethod
    def _human_size(size_bytes):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
class ProgressCallback:
    """Shows a simple progress bar during upload/download."""

    def __init__(self, total_size):
        self._total = total_size
        self._seen = 0

    def __call__(self, bytes_amount):
        self._seen += bytes_amount
        pct = (self._seen / self._total) * 100 if self._total else 0
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"\r  [{bar}] {pct:.1f}%", end="", flush=True)        