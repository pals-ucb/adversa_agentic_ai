# File: src/stores/s3_store.py

import json
import boto3
from botocore.exceptions import ClientError
from typing import Type, TypeVar, Generic, Optional, List
from uuid import UUID
from pydantic import BaseModel
from ..schemas.sim_models import SimModel  # adjust if needed

T = TypeVar("T", bound=BaseModel)

class S3Store(Generic[T]):
    def __init__(self, bucket: str, prefix: str, model_cls: Type[T]):
        """
        bucket: the S3 bucket name (e.g. "aaa-sim-data-12345")
        prefix: subfolder key prefix, e.g. "sim_models/"
        model_cls: Pydantic class for deserialization (SimModel or PromptTemplate)
        """
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/"
        self.model_cls = model_cls

    def _key(self, obj_id: str) -> str:
        return f"{self.prefix}{obj_id}.json"

    def save(self, obj: T) -> T:
        body = obj.model_dump_json()  # for Pydantic v2
        key = self._key(str(obj.id))
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType="application/json")
        return obj

    def load(self, obj_id: str) -> Optional[T]:
        key = self._key(obj_id)
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            data = json.loads(response["Body"].read())
            return self.model_cls(**data)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def delete(self, obj_id: str) -> None:
        key = self._key(obj_id)
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            # if key does not exist, ignore
            if e.response["Error"]["Code"] != "NoSuchKey":
                raise

    def list_all(self) -> List[T]:
        # List objects under prefix
        paginator = self.s3.get_paginator("list_objects_v2")
        items: List[T] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".json"):
                    # Read each object
                    resp = self.s3.get_object(Bucket=self.bucket, Key=key)
                    data = json.loads(resp["Body"].read())
                    items.append(self.model_cls(**data))
        return items

    def list_summaries(self) -> List[dict]:
        summaries = []
        for item in self.list_all():
            summaries.append({"id": str(item.id), "name": getattr(item, "name", "")})
        return summaries
