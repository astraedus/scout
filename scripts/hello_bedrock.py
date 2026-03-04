"""
Minimal AWS Bedrock Nova 2 Lite test script.
Usage: python scripts/hello_bedrock.py
Requires AWS credentials in .env or AWS default credential chain.
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing AWS Bedrock (Nova 2 Lite)...")

try:
    import boto3

    aws_region = os.getenv("AWS_REGION", "us-east-1")
    model_id = "amazon.nova-lite-v1:0"

    client = boto3.client(
        "bedrock-runtime",
        region_name=aws_region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
    )

    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Say 'Hello from Nova 2 Lite!' and nothing else."}],
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 50,
            "temperature": 0.0,
        },
    })

    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    response_body = json.loads(response["body"].read())
    text = response_body["output"]["message"]["content"][0]["text"]
    print(f"Nova 2 Lite response: {text}")
    print("Bedrock test PASSED.")

except ImportError:
    print("ERROR: boto3 not installed. Run: pip install boto3")
except Exception as e:
    print(f"ERROR: Bedrock test failed: {e}")
    print("Check your AWS credentials and that Bedrock is enabled in your region.")
