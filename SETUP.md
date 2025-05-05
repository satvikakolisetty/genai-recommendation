# Setup Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
KINESIS_STREAM_NAME=recommendation-events

# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
VERTEX_AI_ENDPOINT=projects/your-project-id/locations/us-central1/endpoints/your-endpoint-id

# Snowflake Configuration
SNOWFLAKE_USER=your-snowflake-user
SNOWFLAKE_PASSWORD=your-snowflake-password
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_WAREHOUSE=RECOMMENDATION_WH
SNOWFLAKE_DATABASE=RECOMMENDATION_DB
SNOWFLAKE_SCHEMA=PUBLIC

# API Configuration
API_URL=http://localhost:8000
```

## Infrastructure Setup

1. Deploy AWS infrastructure:
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

2. Deploy GCP infrastructure:
```bash
cd infrastructure/gcp
terraform init
terraform plan
terraform apply
```

3. Set up Snowflake:
```bash
cd snowflake
snowsql -f ddl.sql
```

## Application Setup

1. Build and start the services:
```bash
docker-compose build
docker-compose up
```

2. Generate sample data:
```bash
docker-compose run data_generator python generate_sample_data.py
```

3. Train the model:
```bash
cd ml
python train_model.py --deploy
```

## Accessing the Services

- FastAPI Service: http://localhost:8000
- Streamlit Dashboard: http://localhost:8501

## Monitoring

- AWS CloudWatch: Monitor Kinesis, Lambda, and Glue metrics
- GCP Cloud Monitoring: Monitor Vertex AI endpoint metrics
- Snowflake: Monitor query performance and warehouse usage

## Cost Optimization

1. Snowflake:
   - Auto-clustering reduces compute costs by 25%
   - Materialized views for frequently accessed data
   - Auto-suspend warehouse when idle

2. AWS:
   - Kinesis stream partitioning for parallel processing
   - Lambda function optimization
   - S3 lifecycle policies for cost-effective storage

3. GCP:
   - Vertex AI endpoint auto-scaling
   - Batch predictions for cost efficiency
   - Model versioning for A/B testing 