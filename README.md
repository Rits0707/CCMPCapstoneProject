CCMPCapstoneProject  
Serverless Image Processing Pipeline – Capstone Project

This project is the final capstone for the Cloud Computing and Modern Platforms course. It demonstrates a fully serverless image-processing workflow using AWS services such as S3, Lambda, Step Functions, and API Gateway.

-----------------------------------------------------------------------------------------
PROJECT OVERVIEW

This application automatically resizes images stored in an S3 input bucket and saves the resized version into a second S3 output bucket.

The workflow is triggered externally through API Gateway, which starts a Step Functions state machine that coordinates the Lambda image-processing function.

-----------------------------------------------------------------------------------------
HIGH-LEVEL ARCHITECTURE

API Gateway  
→ Step Functions  
→ Lambda (Pillow layer)  
→ S3 Resized Bucket  
← CloudWatch Logs

Architecture Diagram (ASCII)

 +-----------------+   +-----------------+   +--------------------+   +-----------------+  
 |   API Gateway   |-->|  Step Functions |-->|   Lambda Function  |-->|       S3        | 
  +-----------------+   +-----------------+   +--------------------+   +-----------------
  +                                  ^                                  
                                     |                            
                            +-----------------+                            
                            |   CloudWatch    |                            
                            +-----------------+ 

-----------------------------------------------------------------------------------------
PREREQUISITES

AWS Requirements:
• AWS Account  
• Ability to create S3 buckets, IAM roles, Lambda, Lambda Layers, Step Functions, API Gateway  

Lambda Dependencies:
• Pillow (Python) via Lambda Layer  

Local Tools:
• Python 3.x  
• AWS CLI (optional)  
• Git and GitHub repo  

-----------------------------------------------------------------------------------------
DEPLOYMENT INSTRUCTIONS

1. CREATE TWO S3 BUCKETS

Original Images Bucket:
s3-bucket-original-images

Resized Images Bucket:
s3-bucket-resized-images

------------------------------------------------------
2. BUILD AND UPLOAD THE PILLOW LAYER

mkdir python  
pip install pillow -t python/  
zip -r pillow-layer.zip python  

Upload:
Lambda → Layers → Create Layer → Upload ZIP → Python 3.10  
Attach layer to Lambda.

------------------------------------------------------
3. CREATE THE LAMBDA FUNCTION

Runtime: Python 3.10  
Handler: handler.lambda_handler  

IAM Permissions Needed:

Allow Get/Put on original bucket:
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::s3-bucket-original-images/*"
}

Allow Put on resized bucket:
{
  "Effect": "Allow",
  "Action": ["s3:PutObject"],
  "Resource": "arn:aws:s3:::s3-bucket-resized-images/*"
}

Upload handler.py  
Attach Pillow layer  

------------------------------------------------------
4. CREATE STEP FUNCTIONS STATE MACHINE

Name:
CCMP-ImageProcessingStateMachine

Your ARN:
arn:aws:states:us-east-2:175748411785:stateMachine:CCMP-ImageProcessingStateMachine

Definition:
{
  "Comment": "Image Processing Workflow",
  "StartAt": "ResizeImage",
  "States": {
    "ResizeImage": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-2:175748411785:function:ProcessImage",
      "End": true
    }
  }
}

------------------------------------------------------
5. CREATE IAM ROLE (API GATEWAY → STEP FUNCTIONS)

Role Name:
APIGatewayToStepFunctions

Trust Policy:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "apigateway.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}

Permissions:
{
  "Effect": "Allow",
  "Action": "states:StartExecution",
  "Resource": "arn:aws:states:us-east-2:175748411785:stateMachine:CCMP-ImageProcessingStateMachine"
}

------------------------------------------------------
6. CONFIGURE API GATEWAY

Path:
/start-image-processing

Integration:
AWS Service → Step Functions  
Action: StartExecution  

Execution Role:
arn:aws:iam::175748411785:role/APIGatewayToStepFunctions

------------------------------------------------------
7. RUNNING THE API

Invoke URL:
https://your-api-id.execute-api.us-east-2.amazonaws.com/prod/start-image-processing

POST Body:
{
  "stateMachineArn": "arn:aws:states:us-east-2:175748411785:stateMachine:CCMP-ImageProcessingStateMachine",
  "input": "{"bucket":"s3-bucket-original-images","key":"input/Flint.jpg"}"
}

Expected Response:
{
  "executionArn": "arn:aws:states:us-east-2:175748411785:execution:CCMP-ImageProcessingStateMachine:<execution-id>",
  "startDate": 1763677602.443
}

Resized output appears in:
s3-bucket-resized-images/output/

------------------------------------------------------
HOW TO RUN THE APPLICATION

METHOD 1: API Gateway Test Console  
• Navigate to your API method  
• Select Test  
• Paste the JSON body  
• Click Test  

METHOD 2: Postman  
POST → Invoke URL  
Body → Raw → JSON  
Paste JSON body  

METHOD 3: cURL  
curl -X POST https://<api-id>.execute-api.us-east-2.amazonaws.com/prod/start-image-processing -H "Content-Type: application/json" -d '{"stateMachineArn":"arn:aws:states:us-east-2:175748411785:stateMachine:CCMP-ImageProcessingStateMachine","input":"{"bucket":"s3-bucket-original-images","key":"input/Flint.jpg"}"}'

Verify in:
• Step Functions Execution History  
• CloudWatch Logs  
• S3 output bucket  

-----------------------------------------------------------------------------------------
SERVICES USED

API Gateway – Public REST endpoint  
Step Functions – Workflow orchestration  
Lambda – Image processing (Pillow)  
S3 Original Bucket – Input images  
S3 Resized Bucket – Output images  
CloudWatch – Logging  
IAM – Security roles  

-----------------------------------------------------------------------------------------
WORKFLOW SUMMARY

1. User sends POST request to API Gateway  
2. API Gateway calls StartExecution  
3. Step Functions invokes Lambda  
4. Lambda loads Pillow, processes image, writes to S3  
5. Logs stored in CloudWatch  

-----------------------------------------------------------------------------------------
