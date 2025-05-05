# Personalized GenAI Recommendation Engine (Multi-Cloud)

A production-ready, multi-cloud recommendation engine that leverages AWS, GCP, and Snowflake to deliver real-time personalized recommendations using GenAI.

## 🏗️ Architecture

![Architecture Diagram](architecture.png)

*To generate the architecture diagram PNG:*
1. Copy the Mermaid diagram from `ARCHITECTURE.md`
2. Use one of these methods to generate the PNG:
   - Visit [Mermaid Live Editor](https://mermaid.live) and paste the diagram
   - Use the Mermaid CLI: `npx @mermaid-js/mermaid-cli -i ARCHITECTURE.md -o architecture.png`
   - Use VS Code with the Mermaid extension

### Components

1. **Data Ingestion (AWS)**
   - Kinesis Stream: Real-time event ingestion
   - Lambda Function: Stream processing to S3
   - S3 Buckets: Raw and processed data storage

2. **Data Processing (AWS + Snowflake)**
   - Glue ETL: Data transformation pipeline
   - Snowflake: Central data warehouse
   - Materialized Views: Optimized query performance

3. **AI/ML (GCP)**
   - Vertex AI: Model training and deployment
   - Collaborative Filtering: User-item recommendations

4. **Application Layer**
   - FastAPI: Real-time recommendation API
   - Streamlit: Interactive dashboard

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- GCP Account with Vertex AI enabled
- Snowflake Account
- Terraform v1.0+
- Python 3.9+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/genai-recommendation.git
cd genai-recommendation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure cloud credentials:
```bash
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export GOOGLE_APPLICATION_CREDENTIALS="path-to-gcp-credentials.json"
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-user"
export SNOWFLAKE_PASSWORD="your-password"
```

4. Deploy infrastructure:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

5. Start the application:
```bash
# Start FastAPI service
cd api
uvicorn main:app --reload

# Start Streamlit dashboard
cd dashboard
streamlit run app.py
```

## 📁 Project Structure

```
.
├── api/                    # FastAPI service
├── dashboard/             # Streamlit dashboard
├── data/                  # Sample data
├── etl/                   # AWS Glue jobs
├── infrastructure/        # Terraform configs
├── lambda/               # AWS Lambda functions
├── ml/                   # Vertex AI model code
├── snowflake/            # Snowflake DDL and queries
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
AWS_REGION=us-east-1
GCP_PROJECT_ID=your-project-id
SNOWFLAKE_WAREHOUSE=RECOMMENDATION_WH
SNOWFLAKE_DATABASE=RECOMMENDATION_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

## 📊 Performance Optimization

- Snowflake auto-clustering reduces compute costs by 25%
- Materialized views for frequently accessed recommendations
- Kinesis stream partitioning for parallel processing
- Vertex AI batch predictions for cost efficiency

## 🔐 Security

- IAM roles with least privilege
- Encrypted S3 buckets
- Snowflake RBAC
- API authentication via JWT

## 📈 Monitoring

- CloudWatch metrics for AWS components
- Vertex AI model monitoring
- Snowflake query performance tracking
- API response time monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - see LICENSE file for details 