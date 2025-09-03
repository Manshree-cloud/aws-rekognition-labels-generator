#!/usr/bin/env python3
"""
AWS Rekognition Labels Generator
--------------------------------
Detects labels for an image stored in S3 using Amazon Rekognition.
Usage:
    python app.py --bucket <bucket-name> --key <object-key> [--max-labels 10] [--min-confidence 80] [--profile default] [--region us-east-1]
"""

import argparse
import boto3
from botocore.exceptions import BotoCoreError, ClientError

def detect_labels(bucket: str, key: str, max_labels: int = 10, min_confidence: float = 80.0, profile: str | None = None, region: str | None = None):
    """Call Rekognition.detect_labels for an S3 object and return labels."""
    try:
        if profile:
            boto3.setup_default_session(profile_name=profile, region_name=region)
        elif region:
            boto3.setup_default_session(region_name=region)
        client = boto3.client("rekognition")
        resp = client.detect_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MaxLabels=max_labels,
            MinConfidence=min_confidence,
        )
        return resp.get("Labels", [])
    except (BotoCoreError, ClientError) as e:
        raise SystemExit(f"ERROR: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate labels for an S3 image using Amazon Rekognition.")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--key", required=True, help="S3 object key (path/filename.jpg)")
    parser.add_argument("--max-labels", type=int, default=10, help="Maximum labels to return (default: 10)")
    parser.add_argument("--min-confidence", type=float, default=80.0, help="Minimum confidence threshold (default: 80.0)")
    parser.add_argument("--profile", default=None, help="AWS profile name to use (optional)")
    parser.add_argument("--region", default=None, help="AWS region to use (optional)")
    args = parser.parse_args()

    labels = detect_labels(
        bucket=args.bucket,
        key=args.key,
        max_labels=args.max_labels,
        min_confidence=args.min_confidence,
        profile=args.profile,
        region=args.region,
    )

    if not labels:
        print("No labels found.")
        return

    print(f"Labels for s3://{args.bucket}/{args.key}:")
    for l in labels:
        name = l.get("Name")
        conf = l.get("Confidence")
        parents = [p.get("Name") for p in l.get("Parents", [])]
        parents_str = f" (parents: {', '.join(parents)})" if parents else ""
        print(f"- {name}: {conf:.2f}%{parents_str}")

if __name__ == "__main__":
    main()