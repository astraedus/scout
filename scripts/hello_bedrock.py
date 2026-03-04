"""
Minimal Bedrock Nova 2 Lite test script.
Usage: python scripts/hello_bedrock.py
Requires AWS credentials configured (aws configure or env vars).
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

print("Testing Bedrock Nova 2 Lite connection...")

try:
    import boto3

    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    model_id = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")

    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": "What is 2+2? Reply with just the number."}],
            }
        ],
    )

    answer = response["output"]["message"]["content"][0]["text"]
    print(f"Nova 2 Lite response: {answer}")
    print("Bedrock test PASSED.")

except ImportError:
    print("ERROR: boto3 not installed. Run: pip install boto3")
except Exception as e:
    print(f"ERROR: Bedrock test failed: {e}")
    print("Make sure AWS credentials are configured: aws configure")
