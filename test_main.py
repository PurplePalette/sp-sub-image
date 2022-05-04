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
    ("filetype", "filepath"),
    [
        ("LevelCover", "./test_assets/red_2_1.png"),
        ("LevelCover", "./test_assets/blue_1_2.png"),
        ("LevelCover", "./test_assets/green_1_1.png"),
        ("EngineThumbnail", "./test_assets/red_2_1.png"),
        ("SkinThumbnail", "./test_assets/red_2_1.png"),
        ("EffectThumbnail", "./test_assets/red_2_1.png"),
        ("ParticleThumbnail", "./test_assets/red_2_1.png"),
    ],
)
def test_post_convert(filetype: str, filepath: str):
    with open(filepath, "rb") as f:
        image_hash = hashlib.sha1(f.read()).hexdigest()
        f.seek(0)
        s3_bucket.put_object(Key=filetype + "/" + image_hash, Body=f)
    response = client.post("/convert", json={"type": filetype, "hash": image_hash})
    response_hash = response.json()["hash"]
    assert response.status_code == 200
    modified_data = s3_bucket.Object(filetype + "/" + response_hash).get()["Body"]
    assert hashlib.sha1(modified_data.read()).hexdigest() == response_hash
