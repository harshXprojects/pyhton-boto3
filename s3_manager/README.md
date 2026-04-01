# 🪣 S3 Manager CLI

A boto3-powered command-line tool for managing S3 buckets and objects.

## Setup

```bash
pip install -r requirements.txt
aws configure   # set your Access Key, Secret, and region
```

## Usage

```bash
# List all your buckets
python cli.py list-buckets

# Create a new bucket
python cli.py create-bucket my-new-bucket

# List objects in a bucket (optional prefix filter)
python cli.py list-objects my-bucket --prefix images/

# Upload a file (optionally set a custom S3 key)
python cli.py upload ./photo.jpg my-bucket --key photos/2024/photo.jpg

# Download a file
python cli.py download my-bucket photos/2024/photo.jpg --output ./photo.jpg

# Delete an object (prompts for confirmation)
python cli.py delete my-bucket photos/old.jpg

# Generate a presigned URL (valid for 1 hour by default)
python cli.py presign my-bucket photos/photo.jpg --expiry 7200

# Copy an object to another bucket
python cli.py copy src-bucket file.txt dst-bucket --dst-key archive/file.txt
```

## Global Options

| Flag        | Description                        |
|-------------|------------------------------------|
| `--profile` | AWS CLI profile name               |
| `--region`  | AWS region (default: `us-east-1`)  |

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
s3_manager/
├── cli.py                  # CLI entry point
├── requirements.txt
├── s3manager/
│   ├── __init__.py
│   └── client.py           # S3Manager class
└── tests/
    └── test_s3manager.py   # Unit tests (mocked boto3)
```
