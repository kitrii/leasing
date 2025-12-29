import json

from minio import Minio
import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "equipment")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,  # True если используешь https
    cert_check=False
)


import json
from minio import Minio
from minio.error import S3Error


def ensure_public_bucket(client: Minio, bucket_name: str):
    """
    Создаёт бакет, если его нет,
    и делает его публичным (GET only)
    """
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }

        client.set_bucket_policy(bucket_name, json.dumps(policy))

    except S3Error as e:
        raise RuntimeError(f"MinIO bucket error: {e}")

