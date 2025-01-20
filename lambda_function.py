import boto3
import json
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Clients
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
mediaconvert = boto3.client('mediaconvert')
cloudfront = boto3.client('cloudfront')

# Bucket and folder names
UPLOAD_BUCKET = 'your-upload-bucket-name'
PROCESSED_BUCKET = 'your-processed-bucket-name'
DISTRIBUTION_ID = 'your-cloudfront-distribution-id'

# Lambda function to trigger video transcoding
def lambda_handler(event, context):
    try:
        # Get uploaded file details
        for record in event['Records']:
            s3_object_key = record['s3']['object']['key']
            logger.info(f"New file uploaded: {s3_object_key}")

            # Start transcoding job
            transcode_video(s3_object_key)
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise e

# Function to initiate video transcoding
def transcode_video(input_key):
    try:
        # Fetch the MediaConvert endpoint
        endpoint = mediaconvert.describe_endpoints()['Endpoints'][0]['Url']
        mediaconvert_client = boto3.client('mediaconvert', endpoint_url=endpoint)

        # Create the MediaConvert job
        response = mediaconvert_client.create_job(
            Role='arn:aws:iam::your-account-id:role/MediaConvertRole',
            Settings={
                "Inputs": [
                    {
                        "FileInput": f"s3://{UPLOAD_BUCKET}/{input_key}",
                        "AudioSelectors": {
                            "Audio Selector 1": {
                                "DefaultSelection": "DEFAULT"
                            }
                        },
                        "VideoSelector": {},
                        "TimecodeSource": "EMBEDDED"
                    }
                ],
                "OutputGroups": [
                    {
                        "Name": "File Group",
                        "OutputGroupSettings": {
                            "Type": "FILE_GROUP_SETTINGS",
                            "FileGroupSettings": {
                                "Destination": f"s3://{PROCESSED_BUCKET}/output/"
                            }
                        },
                        "Outputs": [
                            {
                                "ContainerSettings": {
                                    "Container": "MP4"
                                },
                                "VideoDescription": {
                                    "CodecSettings": {
                                        "Codec": "H_264",
                                        "H264Settings": {
                                            "Bitrate": 5000000,
                                            "FramerateControl": "SPECIFIED",
                                            "FramerateNumerator": 30,
                                            "FramerateDenominator": 1
                                        }
                                    }
                                },
                                "AudioDescriptions": [
                                    {
                                        "CodecSettings": {
                                            "Codec": "AAC",
                                            "AacSettings": {
                                                "Bitrate": 96000,
                                                "SampleRate": 48000,
                                                "CodingMode": "CODING_MODE_2_0"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        )

        logger.info(f"MediaConvert job created: {response['Job']['Id']}")
    except Exception as e:
        logger.error(f"Error starting MediaConvert job: {str(e)}")
        raise e

# Frontend (React) and deployment details can be added separately.
# Use CloudFront for CDN distribution after transcoding is complete.
