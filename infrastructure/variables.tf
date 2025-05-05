# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# GCP Configuration
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

# Kinesis Configuration
variable "kinesis_stream_name" {
  description = "Name of the Kinesis stream"
  type        = string
  default     = "recommendation-events"
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis stream"
  type        = number
  default     = 1
}

# S3 Configuration
variable "raw_bucket_name" {
  description = "Name of the raw data S3 bucket"
  type        = string
  default     = "recommendation-raw-data"
}

variable "processed_bucket_name" {
  description = "Name of the processed data S3 bucket"
  type        = string
  default     = "recommendation-processed-data"
}

# Lambda Configuration
variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "kinesis-to-s3-processor"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.9"
}

variable "lambda_handler" {
  description = "Lambda handler function"
  type        = string
  default     = "lambda_function.lambda_handler"
}

# Glue Configuration
variable "glue_job_name" {
  description = "Name of the Glue job"
  type        = string
  default     = "recommendation-etl"
}

variable "glue_role_name" {
  description = "Name of the IAM role for Glue"
  type        = string
  default     = "recommendation-glue-role"
}

# Vertex AI Configuration
variable "vertex_ai_model_name" {
  description = "Name of the Vertex AI model"
  type        = string
  default     = "recommendation-model"
}

variable "vertex_ai_endpoint_name" {
  description = "Name of the Vertex AI endpoint"
  type        = string
  default     = "recommendation-endpoint"
}

variable "vertex_ai_machine_type" {
  description = "Machine type for Vertex AI endpoint"
  type        = string
  default     = "n1-standard-4"
} 