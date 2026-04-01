import pytest
from unittest.mock import patch, MagicMock,mock_open
from datetime import datetime
from s3_manager import S3Manager

@pytest.fixture
def s3_manager():
    with patch("boto3.Session") as mock_session:
        mock_s3 = MagicMock()
        mock_session.return_value.client.return_value = mock_s3
        mgr = S3Manager()
        mgr.s3 = mock_s3
        return mgr

class TestListBuckets:
    def test_returns_bucket_names(self, manager):
        manager.s3.list_buckets.return_value = {
            "Buckets": [{"Name": "bucket-a"}, {"Name": "bucket-b"}]
        }
        result = manager.list_buckets()
        assert result == ["bucket-a", "bucket-b"]
    def test_empty_account(self, manager):
        manager.s3.list_buckets.return_value = {"Buckets": []}
        assert manager.list_buckets() == []

class TestListObjects:
    def test_paginates_correctly(self, manager):
        paginator = MagicMock()
        manager.s3.get_paginator.return_value = paginator
        paginator.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "file1.txt", "Size": 1024, "LastModified": datetime(2024, 1, 1, 12, 0)},
                    {"Key": "file2.jpg", "Size": 204800, "LastModified": datetime(2024, 3, 15, 8, 30)},
                ]
            }
        ]
        objects = manager.list_objects("my-bucket")
        assert len(objects) == 2
        assert objects[0]["key"] == "file1.txt"
        assert objects[0]["size"] == 1024
        assert objects[1]["key"] == "file2.jpg"

    def test_empty_bucket(self, manager):
        paginator = MagicMock()
        manager.s3.get_paginator.return_value = paginator
        paginator.paginate.return_value = [{}]  # No "Contents" key
        assert manager.list_objects("empty-bucket") == []
        
class TestUploadFile:
    def test_upload_success(self, manager, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        manager.upload_file(str(test_file), "my-bucket")

        manager.s3.upload_file.assert_called_once()
        call_args = manager.s3.upload_file.call_args
        assert call_args[0][1] == "my-bucket"
        assert call_args[0][2] == "test.txt"  # default key = filename

    def test_upload_custom_key(self, manager, tmp_path):
        test_file = tmp_path / "local.txt"
        test_file.write_text("data")

        manager.upload_file(str(test_file), "my-bucket", s3_key="folder/remote.txt")

        call_args = manager.s3.upload_file.call_args
        assert call_args[0][2] == "folder/remote.txt"

    def test_upload_missing_file_raises(self, manager):
        with pytest.raises(FileNotFoundError):
            manager.upload_file("/nonexistent/file.txt", "my-bucket")

class TestDeleteObject:
    def test_delete_calls_correct_args(self, manager):
        manager.delete_object("my-bucket", "some/file.txt")
        manager.s3.delete_object.assert_called_once_with(
            Bucket="my-bucket", Key="some/file.txt"
        )


class TestPresignedUrl:
    def test_returns_url(self, manager):
        manager.s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/signed"
        url = manager.presigned_url("my-bucket", "file.txt", expiry=600)

        assert url == "https://s3.amazonaws.com/signed"
        manager.s3.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "my-bucket", "Key": "file.txt"},
            ExpiresIn=600,
        )


class TestHumanSize:
    @pytest.mark.parametrize("size,expected", [
        (500, "500.0 B"),
        (1024, "1.0 KB"),
        (1048576, "1.0 MB"),
        (1073741824, "1.0 GB"),
    ])
    def test_human_size(self, size, expected):
        assert S3Manager._human_size(size) == expected



    
