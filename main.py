import hashlib
import os
import traceback
from io import BytesIO

import boto3
import botocore
import botocore.exceptions
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

load_dotenv()


class ConvertParams(BaseModel):
    hash: str


app = FastAPI()
s3_endpoint = os.getenv("S3_ENDPOINT")
s3 = boto3.resource(
    "s3", endpoint_url=s3_endpoint, aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET")
)
s3_bucket = s3.Bucket(os.getenv("S3_BUCKET"))


@app.exception_handler(Exception)
async def exception_handler(_request: Request, exc: Exception):
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    return JSONResponse(status_code=500, content={"code": "internal_server_error", "message": "Internal server error"})


@app.get("/")
async def get_root():
    return {
        "status": "ok",
    }


@app.post("/convert")
async def post_convert(item: ConvertParams):
    object = s3_bucket.Object("LevelCover/" + item.hash)
    try:
        body = object.get()["Body"]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(404, {"status": "file_not_found", "message": "File not found"})
        else:
            raise
    image = Image.open(body)
    if image.size[0] == image.size[1]:
        processed_image = image.resize((512, 512))
    else:
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
    s3_bucket.put_object(
        Key="LevelCover/" + image_hash,
        Body=image_io.getvalue(),
        ContentType="image/png",
    )
    return {
        "hash": image_hash,
    }
