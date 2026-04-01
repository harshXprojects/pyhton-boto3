#!/usr/bin/env python3

import argparse
import sys
from s3manager.client import S3Manager

def get_manager(args):
    return S3Manager(
        profile_name=getattr(args, "profile", None),
        region_name=getattr(args,"region", "us-east-1"),
    )

def cmd_list_buckets(args):
    manager = get_manager(args)
    buckets = manager.list_buckets()
    if not buckets:
        print("No buckets found.")
    else:
        print(f"\n{'BUCKET NAME':<40} ")
        print("─" * 42)
        for b in buckets:
            print(f"  {b}")
        print(f"\n{len(buckets)} bucket(s) total.")

def cmd_create_bucket(args):
    manager = get_manager(args)
    manager.create_bucket(args.bucket)

def cmd_list_objects(args):
    manager = get_manager(args)
    objects = manager.list_objects(args.bucket, prefix=args.prefix or "")
    if not objects:
        print(f"No objects found in '{args.bucket}'.")
        return
    print(f"\n{'KEY':<50} {'SIZE':>10}  {'LAST MODIFIED'}")
    print("─" * 80)
    for obj in objects:
        print(f"  {obj['key']:<48} {obj['size']:>10,}  {obj['last_modified']}")
    print(f"\n{len(objects)} object(s) total.")

def cmd_upload(args):
    manager = get_manager(args)
    manager.upload_file(args.file, args.bucket, s3_key=args.key)
    
def cmd_download(args):
    manager = get_manager(args)
    manager.download_file(args.bucket, args.key, local_path=args.output)

def delete_object(args):
    confirm = input(f" ⚠️ Are you sure you want to delete 's3://{args.bucket}/{args.key}'? [y/N]: ")
    if confirm.lower() in ("y", "yes"):
        manager = get_manager(args)
        manager.delete_object(args.bucket, args.key)
        print(f"Object 's3://{args.bucket}/{args.key}' deleted.")
    else:
        print("Operation cancelled.")

def cmd_presign(args):
    manager = get_manager(args)
    url = manager.generate_presigned_url(args.bucket, args.key, expiry=args.expiry)
    print(f"Presigned URL (expires in {args.expiry} seconds):\n{url}")
    
def cmd_copy(args):
    manager = get_manager(args)
    manager.copy_object(args.source_bucket, args.source_key, args.dest_bucket, args.dest_key)
    print(f"Object copied from 's3://{args.source_bucket}/{args.source_key}' to 's3://{args.dest_bucket}/{args.dest_key}'.")

def build_parser():
    parser = argparse.ArgumentParser(
        prog="s3manager",
        description="A simple CLI tool for managing S3 buckets and objects.",
    )
    
    parser.add_argument("--profile", help="AWS CLI profile to use", default=None)
    parser.add_argument("--region", help="AWS region (default: us-east-1)", default="us-east-1")
    
    sub = parser.add_subparsers(dest="commands", required=True)
    
    sub.add_parser("list-buckets", help="List all S3 buckets")
    
    p = sub.add_parser("create-bucket", help="Create a new S3 bucket")
    p.add_argument("bucket", help="Name of the bucket to create")
    
    p = sub.add_parser("list-objects", help="List objects in a bucket")
    p.add_argument("bucket", help="Name of the bucket")
    p.add_argument("--prefix", help="Filter objects by prefix", default="")
    
    p = sub.add_parser("upload", help="Upload a file to S3")
    p.add_argument("file", help="Path to the local file to upload")
    p.add_argument("bucket", help="Name of the target bucket")
    p.add_argument("--key", help="S3 key (defaults to local filename)", default=None)
    
    p = sub.add_parser("download", help="Download a file from S3")
    p.add_argument("bucket", help="Name of the bucket")
    p.add_argument("key", help="S3 key of the object to download")
    p.add_argument("--output", help="Local path to save the downloaded file (defaults to current directory)", default=None)
    
    p = sub.add_parser("delete", help="Delete an object from S3")
    p.add_argument("bucket", help="Name of the bucket")
    p.add_argument("key", help="S3 key of the object to delete")
    
    p = sub.add_parser("presign", help="Generate a presigned URL for an S3 object")
    p.add_argument("bucket", help="Name of the bucket")
    p.add_argument("key", help="S3 key of the object")
    p.add_argument("--expiry", type=int, help="URL expiry time in seconds (default: 3600)", default=3600)
    
    p = sub.add_parser("copy", help="Copy an object within or across buckets")
    p.add_argument("source_bucket", help="Name of the source bucket")
    p.add_argument("source_key", help="S3 key of the source object")
    p.add_argument("dest_bucket", help="Name of the destination bucket")
    p.add_argument("--dest_key", help="S3 key for the copied object", default=None)
    
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    handlers = {
        "list-buckets": cmd_list_buckets,
        "create-bucket": cmd_create_bucket,
        "list-objects": cmd_list_objects,
        "upload": cmd_upload,
        "download": cmd_download,
        "delete": delete_object,
        "presign": cmd_presign,
        "copy": cmd_copy,
    }
    
    try:
        handlers[args.commands](args)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()