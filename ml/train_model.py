import os
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_recommenders as tfrs
from google.cloud import aiplatform
from datetime import datetime
import argparse

def load_data_from_snowflake():
    """Load training data from Snowflake."""
    import snowflake.connector
    
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            USER_ID,
            ITEM_ID,
            INTERACTION_COUNT,
            INTERACTION_TYPES
        FROM USER_ITEM_INTERACTIONS_MV
    """)
    
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['user_id', 'item_id', 'interaction_count', 'interaction_types'])
    conn.close()
    
    return df

def create_model(user_ids, item_ids, embedding_dim=64):
    """Create a collaborative filtering model."""
    class RecommendationModel(tfrs.Model):
        def __init__(self):
            super().__init__()
            
            # User embeddings
            self.user_model = tf.keras.Sequential([
                tf.keras.layers.StringLookup(
                    vocabulary=user_ids,
                    mask_token=None
                ),
                tf.keras.layers.Embedding(
                    len(user_ids) + 1,
                    embedding_dim
                )
            ])
            
            # Item embeddings
            self.item_model = tf.keras.Sequential([
                tf.keras.layers.StringLookup(
                    vocabulary=item_ids,
                    mask_token=None
                ),
                tf.keras.layers.Embedding(
                    len(item_ids) + 1,
                    embedding_dim
                )
            ])
            
            # Task
            self.task = tfrs.tasks.Retrieval(
                metrics=tfrs.metrics.FactorizedTopK(
                    candidates=item_ids.map(
                        lambda x: self.item_model(tf.constant([x]))
                    )
                )
            )
        
        def compute_loss(self, features, training=False):
            user_embeddings = self.user_model(features["user_id"])
            item_embeddings = self.item_model(features["item_id"])
            
            return self.task(user_embeddings, item_embeddings)
    
    return RecommendationModel()

def train_model():
    """Train the recommendation model."""
    # Load data
    df = load_data_from_snowflake()
    
    # Prepare data
    user_ids = df['user_id'].unique()
    item_ids = df['item_id'].unique()
    
    # Create TensorFlow datasets
    interactions = tf.data.Dataset.from_tensor_slices({
        "user_id": df['user_id'].values,
        "item_id": df['item_id'].values,
        "interaction_count": df['interaction_count'].values
    })
    
    # Create and compile model
    model = create_model(user_ids, item_ids)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.1))
    
    # Train model
    model.fit(
        interactions.batch(4096),
        epochs=10
    )
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"gs://{os.getenv('MODEL_BUCKET')}/models/recommendation_model_{timestamp}"
    model.save(model_path)
    
    return model_path

def deploy_model(model_path):
    """Deploy the model to Vertex AI."""
    aiplatform.init(
        project=os.getenv('GCP_PROJECT_ID'),
        location=os.getenv('GCP_REGION')
    )
    
    # Create model
    model = aiplatform.Model.upload(
        display_name="recommendation_model",
        artifact_uri=model_path,
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-8:latest"
    )
    
    # Deploy model
    endpoint = model.deploy(
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=3
    )
    
    return endpoint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--deploy', action='store_true', help='Deploy model after training')
    args = parser.parse_args()
    
    # Train model
    model_path = train_model()
    print(f"Model saved to: {model_path}")
    
    # Deploy model if requested
    if args.deploy:
        endpoint = deploy_model(model_path)
        print(f"Model deployed to endpoint: {endpoint.resource_name}")

if __name__ == "__main__":
    main() 