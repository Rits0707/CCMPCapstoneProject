import boto3
from io import BytesIO
from PIL import Image
import json

s3 = boto3.client("s3")

ORIGINAL_BUCKET = "s3-bucket-original-images"
RESIZED_BUCKET = "s3-bucket-resized-images"

def lambda_handler(event, context):
    print("Incoming event:", event)

    # 1) Step Functions / API Gateway → State Machine wrapper
    if "stateMachineArn" in event and "input" in event:
        inner = json.loads(event["input"])
        bucket = inner["bucket"]
        key = inner["key"]

    # 2) Step Functions direct input
    elif "bucket" in event and "key" in event:
        bucket = event["bucket"]
        key = event["key"]

    # 3) S3 upload event
    elif "Records" in event and "s3" in event["Records"][0]:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

    else:
        raise ValueError(f"Unexpected event format: {event}")

    try:
        # Download original
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response["Body"].read()

        # Open
        image = Image.open(BytesIO(image_data))

        # Resize to thumbnail width 200px
        new_width = 200
        new_height = int(image.size[1] * (new_width / image.size[0]))
        image = image.resize((new_width, new_height))

        # Save
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG")
        buffer.seek(0)

        # Output name
        output_key = f"{key.split('.')[0]}_resized.jpg"

        # Upload
        s3.put_object(
            Bucket=RESIZED_BUCKET,
            Key=output_key,
            Body=buffer,
            ContentType="image/jpeg"
        )

        return {
            "statusCode": 200,
            "success": True,
            "message": f"Resized image saved to s3://{RESIZED_BUCKET}/{output_key}"
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "success": False,
            "error": str(e)
        }
