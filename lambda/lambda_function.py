import json
import boto3
import base64
from datetime import datetime
import os

s3_client = boto3.client('s3')
s3_bucket = os.environ['S3_BUCKET']

def process_record(record):
    """Process a single Kinesis record and return formatted data."""
    try:
        # Decode the Kinesis record
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)
        
        # Add processing timestamp
        data['processed_at'] = datetime.utcnow().isoformat()
        
        return data
    except Exception as e:
        print(f"Error processing record: {str(e)}")
        return None

def write_to_s3(data, timestamp):
    """Write processed data to S3 with proper partitioning."""
    if not data:
        return
        
    # Create S3 key with date partitioning
    date = datetime.fromisoformat(timestamp).strftime('%Y/%m/%d')
    hour = datetime.fromisoformat(timestamp).strftime('%H')
    s3_key = f"raw/date={date}/hour={hour}/{timestamp}.json"
    
    try:
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
    except Exception as e:
        print(f"Error writing to S3: {str(e)}")

def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        # Process each record in the Kinesis event
        for record in event['Records']:
            processed_data = process_record(record)
            if processed_data:
                write_to_s3(
                    processed_data,
                    processed_data.get('event_time', datetime.utcnow().isoformat())
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed records')
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing records: {str(e)}')
        } 