"""Move assets to object storage.

Revision ID: 0002_storage
Revises: 0001_initial
"""

import os
from collections.abc import Sequence
from datetime import datetime

import boto3
import sqlalchemy as sa
from alembic import op

revision: str = "0002_storage"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def storage():
    return "assets", boto3.client(
        "s3",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL_S3") or None,
        region_name=os.environ.get("AWS_REGION") or None,
    )


def upgrade() -> None:
    bucket, client = storage()
    assets = op.get_bind().execute(sa.text("SELECT id, content_type, data, name FROM assets"))
    for asset in assets:
        client.put_object(
            Body=asset.data,
            Bucket=bucket,
            CacheControl="public, max-age=31536000, immutable",
            ContentDisposition=f'inline; filename="{asset.name}"',
            ContentType=asset.content_type,
            Key=asset.id,
            Metadata={"name": asset.name},
        )
    op.drop_table("assets")


def downgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    bucket, client = storage()
    now = datetime.now().astimezone()
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for item in page.get("Contents", []):
            asset = client.get_object(Bucket=bucket, Key=item["Key"])
            op.get_bind().execute(
                sa.text(
                    "INSERT INTO assets (content_type, data, name, id, updated_at, created_at) "
                    "VALUES (:content_type, :data, :name, :id, :updated_at, :created_at)"
                ),
                {
                    "content_type": asset.get("ContentType", "application/octet-stream"),
                    "created_at": now,
                    "data": asset["Body"].read(),
                    "id": item["Key"],
                    "name": asset.get("Metadata", {}).get("name", "upload"),
                    "updated_at": now,
                },
            )
