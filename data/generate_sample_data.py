import json
import random
import boto3
import time
from datetime import datetime, timedelta
import os
import uuid

# Initialize AWS clients
kinesis = boto3.client('kinesis')
s3 = boto3.client('s3')

# Constants
NUM_USERS = 1000
NUM_ITEMS = 500
INTERACTIONS_PER_USER = 50
INTERACTION_TYPES = ['view', 'click', 'purchase', 'add_to_cart']

def generate_user_id():
    """Generate a unique user ID."""
    return f"user_{uuid.uuid4().hex[:8]}"

def generate_item_id():
    """Generate a unique item ID."""
    return f"item_{uuid.uuid4().hex[:8]}"

def generate_interaction():
    """Generate a single interaction event."""
    return {
        "user_id": generate_user_id(),
        "item_id": generate_item_id(),
        "interaction_type": random.choice(INTERACTION_TYPES),
        "event_time": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        "metadata": {
            "session_id": str(uuid.uuid4()),
            "device_type": random.choice(["mobile", "desktop", "tablet"]),
            "location": random.choice(["US", "UK", "CA", "AU", "DE"]),
            "referrer": random.choice(["direct", "search", "social", "email"])
        }
    }

def send_to_kinesis(interaction):
    """Send interaction to Kinesis stream."""
    try:
        kinesis.put_record(
            StreamName=os.getenv('KINESIS_STREAM_NAME'),
            Data=json.dumps(interaction),
            PartitionKey=interaction['user_id']
        )
    except Exception as e:
        print(f"Error sending to Kinesis: {str(e)}")

def generate_and_send_data():
    """Generate and send sample data."""
    print("Generating sample data...")
    
    # Generate users and items
    users = [generate_user_id() for _ in range(NUM_USERS)]
    items = [generate_item_id() for _ in range(NUM_ITEMS)]
    
    # Generate interactions
    total_interactions = 0
    for user in users:
        for _ in range(INTERACTIONS_PER_USER):
            interaction = {
                "user_id": user,
                "item_id": random.choice(items),
                "interaction_type": random.choice(INTERACTION_TYPES),
                "event_time": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "metadata": {
                    "session_id": str(uuid.uuid4()),
                    "device_type": random.choice(["mobile", "desktop", "tablet"]),
                    "location": random.choice(["US", "UK", "CA", "AU", "DE"]),
                    "referrer": random.choice(["direct", "search", "social", "email"])
                }
            }
            
            send_to_kinesis(interaction)
            total_interactions += 1
            
            # Add some delay to simulate real-world traffic
            time.sleep(random.uniform(0.1, 0.5))
            
            if total_interactions % 1000 == 0:
                print(f"Generated {total_interactions} interactions...")
    
    print(f"Completed generating {total_interactions} interactions")

if __name__ == "__main__":
    generate_and_send_data() 