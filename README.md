# 🪣 S3 File Manager CLI

> A production-style Python CLI tool for managing AWS S3 — built with **boto3**, **argparse**, and **pytest**.

**Built by [Harshmeet Singh](https://github.com/harshXprojects)**

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![boto3](https://img.shields.io/badge/boto3-AWS_SDK-FF9900?logo=amazonaws&logoColor=white)
![pytest](https://img.shields.io/badge/tested_with-pytest-0A9EDC?logo=pytest)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 Overview

S3 File Manager is a command-line interface that wraps the AWS S3 API via **boto3**. It supports the full lifecycle of S3 operations — create buckets, upload/download files with a live progress bar, generate presigned URLs, copy objects across buckets, and more — all from the terminal.

This project demonstrates real-world Python skills: object-oriented design, CLI argument parsing, paginated AWS API calls, transfer callbacks, and proper unit testing with mocked external services.

---

## 🏗️ Project Structure

```
s3_manager/
├── cli.py                  # CLI entry point — argparse subcommands
├── requirements.txt
├── s3manager/
│   ├── __init__.py
│   └── client.py           # S3Manager class — all boto3 logic lives here
└── tests/
    └── test_s3manager.py   # Unit tests with fully mocked boto3
```

---

## ⚙️ How It Works

```
User runs CLI command
        │
        ▼
   cli.py (argparse)
        │  parses subcommand + args
        ▼
  S3Manager (client.py)
        │  boto3 Session → s3 client
        ▼
    AWS S3 API
        │
        ▼
  Response printed to terminal
  (with progress bar for uploads/downloads)
```

The `S3Manager` class is completely decoupled from the CLI — it can be imported and used as a library too.

---

## 🚀 Setup

### Prerequisites
- Python 3.8+
- AWS account with S3 access
- AWS credentials configured

### Install

```bash
git clone https://github.com/harshXprojects/pyhton-boto3.git
cd pyhton-boto3/s3_manager

pip install -r requirements.txt

# Configure your AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, region, output format
```

---

## 📖 Commands

### List all buckets
```bash
python cli.py list-buckets
```
```
BUCKET NAME
──────────────────────────────────────────
  my-app-assets
  backup-bucket-2024
  redbus-media

3 bucket(s) total.
```

---

### Create a bucket
```bash
python cli.py create-bucket my-new-bucket

# In a specific region
python cli.py --region ap-south-1 create-bucket my-new-bucket
```

---

### List objects in a bucket
```bash
python cli.py list-objects my-bucket

# Filter by prefix (like a folder)
python cli.py list-objects my-bucket --prefix images/2024/
```
```
KEY                                                SIZE  LAST MODIFIED
────────────────────────────────────────────────────────────────────────────────
  images/2024/photo.jpg                         2,048,000  2024-03-15 08:30
  images/2024/banner.png                          512,000  2024-03-16 11:45

2 object(s) total.
```

---

### Upload a file
```bash
# Upload with default key (uses local filename)
python cli.py upload ./report.pdf my-bucket

# Upload with a custom S3 key (path inside the bucket)
python cli.py upload ./report.pdf my-bucket --key docs/2024/report.pdf
```
```
⬆️  Uploading 'report.pdf' (2.1 MB) → s3://my-bucket/docs/2024/report.pdf
  [████████████████░░░░] 82.3%
✅ Upload complete.
```

---

### Download a file
```bash
python cli.py download my-bucket docs/2024/report.pdf

# Save to a specific local path
python cli.py download my-bucket docs/2024/report.pdf --output ./downloads/report.pdf
```
```
⬇️  Downloading s3://my-bucket/docs/2024/report.pdf (2.1 MB) → 'report.pdf'
  [████████████████████] 100.0%
✅ Download complete.
```

---

### Delete an object
```bash
python cli.py delete my-bucket docs/old-report.pdf
```
```
⚠️  Are you sure you want to delete 's3://my-bucket/docs/old-report.pdf'? [y/N]: y
🗑️  Deleted s3://my-bucket/docs/old-report.pdf
```

---

### Generate a presigned URL
```bash
# Default expiry: 1 hour (3600 seconds)
python cli.py presign my-bucket docs/report.pdf

# Custom expiry (24 hours)
python cli.py presign my-bucket docs/report.pdf --expiry 86400
```
```
Presigned URL (expires in 86400 seconds):
https://my-bucket.s3.amazonaws.com/docs/report.pdf?X-Amz-Algorithm=...
```

---

### Copy an object
```bash
# Copy within the same bucket
python cli.py copy my-bucket original.txt my-bucket --dest_key archive/original.txt

# Copy across buckets
python cli.py copy source-bucket file.txt destination-bucket --dest_key backup/file.txt
```
```
📋 Copied s3://source-bucket/file.txt → s3://destination-bucket/backup/file.txt
```

---

## 🌐 Global Options

These flags work with every command:

| Flag | Description | Default |
|------|-------------|---------|
| `--profile` | AWS CLI named profile | None (uses default) |
| `--region` | AWS region | `us-east-1` |

```bash
# Use a specific AWS profile and region
python cli.py --profile dev-account --region eu-west-1 list-buckets
```

---

## 🧪 Tests

Tests use `pytest` with **fully mocked boto3** — no real AWS calls are made.

```bash
# Run all tests
pytest tests/ -v

# Run a specific test class
pytest tests/test_s3manager.py::TestUploadFile -v

# Run with coverage report
pytest tests/ -v --cov=s3manager --cov-report=term-missing
```

### What's tested

| Test Class | What It Covers |
|------------|----------------|
| `TestListBuckets` | Returns bucket names, handles empty account |
| `TestListObjects` | Pagination, empty bucket response |
| `TestUploadFile` | Successful upload, custom S3 key, missing file error |
| `TestDeleteObject` | Correct boto3 args passed |
| `TestPresignedUrl` | URL returned, correct params sent |
| `TestHumanSize` | B / KB / MB / GB formatting |

---

## 🔑 Key Technical Concepts Used

**boto3 Session** — Creates an isolated client per profile/region rather than using global credentials, making the tool multi-account safe.

**Paginator** — `list_objects_v2` uses S3 pagination to handle buckets with thousands of objects without hitting API limits.

**Transfer Callback** — `ProgressCallback` class hooks into boto3's upload/download transfer manager to display a live progress bar without blocking I/O.

**argparse subparsers** — Each S3 operation is its own subcommand with its own arguments, making the CLI extensible and self-documenting (`--help` works on every subcommand).

**Mocked unit tests** — `unittest.mock.patch` replaces `boto3.Session` so tests run instantly with no AWS credentials or network access needed.

---

## 👤 Author

**Harshmeet Singh** — B.Tech CSE · DevOps Engineer

[![GitHub](https://img.shields.io/badge/GitHub-harshXprojects-181717?logo=github)](https://github.com/harshXprojects)
