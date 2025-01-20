# Terraform Configuration (main.tf)

provider "aws" {
  region = "us-east-1" # Change to your preferred region
}

# S3 Buckets for video upload and processed output
resource "aws_s3_bucket" "upload_bucket" {
  bucket = "video-upload-bucket"
  acl    = "private"
}

resource "aws_s3_bucket" "processed_bucket" {
  bucket = "video-processed-bucket"
  acl    = "private"
}

# IAM Role for AWS Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      },
    ]
  })

  # Attach policies
  inline_policy {
    name   = "s3-access-policy"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Action   = ["s3:PutObject", "s3:GetObject"],
          Effect   = "Allow",
          Resource = [
            "arn:aws:s3:::video-upload-bucket/*",
            "arn:aws:s3:::video-processed-bucket/*"
          ]
        },
      ]
    })
  }
}

# AWS Lambda Function
resource "aws_lambda_function" "video_processor" {
  filename         = "lambda_function.zip" # Zip file with your Lambda code
  function_name    = "video-processor"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"

  source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      UPLOAD_BUCKET    = "video-upload-bucket"
      PROCESSED_BUCKET = "video-processed-bucket"
    }
  }

  depends_on = [aws_s3_bucket.upload_bucket, aws_s3_bucket.processed_bucket]
}

# Output the bucket names
output "upload_bucket" {
  value = aws_s3_bucket.upload_bucket.bucket
}

output "processed_bucket" {
  value = aws_s3_bucket.processed_bucket.bucket
}

---

# Serverless Framework Configuration (serverless.yml)

service: video-streaming-platform
frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.9
  region: us-east-1 # Update with your preferred region
  iamRoleStatements:
    - Effect: "Allow"
      Action:
          - "s3:GetObject"
          - "s3:PutObject"
      Resource:
          - "arn:aws:s3:::video-upload-bucket/*"
          - "arn:aws:s3:::video-processed-bucket/*"

functions:
  videoProcessor:
    handler: lambda_function.lambda_handler
    events:
      - s3:
          bucket: video-upload-bucket
          event: s3:ObjectCreated:*
    environment:
      UPLOAD_BUCKET: "video-upload-bucket"
      PROCESSED_BUCKET: "video-processed-bucket"

resources:
  Resources:
    UploadBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: video-upload-bucket
    ProcessedBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: video-processed-bucket
