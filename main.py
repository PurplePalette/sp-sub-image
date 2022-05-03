import hashlib
import json
import os
import traceback
import logging
from io import BytesIO

import boto3
import botocore
import botocore.exceptions
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from PIL import Image
from pydantic import BaseModel

load_dotenv()


class ConvertParams(BaseModel):
    hash: str


class ConvertResponse(BaseModel):
    hash: str


def json_response(data, status_code=200):
    return Response(content=json.dumps(data), status_code=status_code, media_type="application/json")


app = FastAPI()
s3_endpoint = os.getenv("S3_ENDPOINT")
s3 = boto3.resource(
    "s3", endpoint_url=s3_endpoint, aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET")
)
s3_bucket = s3.Bucket(os.getenv("S3_BUCKET"))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@app.exception_handler(Exception)
async def exception_handler(_request: Request, exc: Exception):
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    return json_response(
        {"code": "internal_server_error", "message": "Internal server error"},
        500,
    )


@app.get("/")
async def get_root():
    return {
        "status": "ok",
    }


@app.post("/convert")
async def post_convert(item: ConvertParams) -> ConvertResponse:
    logger.info(f"Received request for {item.hash}")
    object = s3_bucket.Object("LevelCover/" + item.hash)
    try:
        logger.info(f"Downloading {item.hash}")
        body = object.get()["Body"]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.info(f"{item.hash} not found, returning 404")
            return json_response({"code": "file_not_found", "message": "File not found"}, 404)
        else:
            raise
    image = Image.open(body)
    if image.size[0] == image.size[1]:
        logger.info(f"{item.hash} is already square, resizing")
        processed_image = image.resize((512, 512))
    else:
        logger.info(f"{item.hash} is not square, modifying")
        color = image.resize((1, 1)).getpixel((0, 0))
        base = Image.new("RGB", (512, 512), color)
        if image.size[0] > image.size[1]:
            resized = image.resize((512, round(512 * (image.size[1] / image.size[0]))))
        else:
            resized = image.resize((round(512 * (image.size[0] / image.size[1])), 512))
        base.paste(resized, (0, (512 - resized.size[1]) // 2))
        processed_image = base
    image_io = BytesIO()
    processed_image.save(image_io, format="PNG")
    image_io.seek(0)

    image_hash = hashlib.sha1(image_io.getvalue()).hexdigest()
    logger.info(f"Uploading {image_hash}")
    s3_bucket.put_object(
        Key="LevelCover/" + image_hash,
        Body=image_io.getvalue(),
        ContentType="image/png",
    )
    logger.info(f"Uploaded {image_hash}")
    return {
        "hash": image_hash,
    }
