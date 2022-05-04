import hashlib
import boto3
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from main import app

load_dotenv()

client = TestClient(app)
s3_endpoint = os.getenv("S3_ENDPOINT")
s3 = boto3.resource(
    "s3", endpoint_url=s3_endpoint, aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET")
)
s3_bucket = s3.Bucket(os.getenv("S3_BUCKET"))


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("filepath", "result_hash"),
    [
        ("./test_assets/red_2_1.png", "fa19c10d5cba06b8c70550a88f8b4e72c84d0bef"),
        ("./test_assets/blue_1_2.png", "17374a3ecdb24dc09aec9086515ad0456a192222"),
        ("./test_assets/green_1_1.png", "66350e3f9150e89003ff579c1b76d5fdd375c91e"),
    ],
)
def test_post_convert(filepath: str, result_hash: str):
    with open(filepath, "rb") as f:
        image_hash = hashlib.sha1(f.read()).hexdigest()
        f.seek(0)
        s3_bucket.put_object(Key="LevelCover/" + image_hash, Body=f)
    response = client.post("/convert", json={"hash": image_hash})
    assert response.status_code == 200
    assert response.json() == {"hash": result_hash}
