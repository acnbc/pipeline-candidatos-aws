import os
import sys
import zipfile

import boto3
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["S3_BUCKET"])
os.environ["S3_BUCKET"] = args["S3_BUCKET"]
os.environ.pop("AWS_PROFILE", None)
os.environ.setdefault("AWS_REGION", "us-east-1")

bucket = args["S3_BUCKET"]
zip_local = "/tmp/pipeline_src.zip"
destino = "/tmp/pipeline_src"
boto3.client("s3").download_file(bucket, "jobs/pipeline_src.zip", zip_local)
with zipfile.ZipFile(zip_local) as z:
    z.extractall(destino)
sys.path.insert(0, destino)

from src.pipeline import executar

executar()