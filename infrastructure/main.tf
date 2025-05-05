terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# AWS Resources
module "aws_infrastructure" {
  source = "./aws"

  # Kinesis
  kinesis_stream_name = var.kinesis_stream_name
  shard_count        = var.kinesis_shard_count

  # S3
  raw_bucket_name      = var.raw_bucket_name
  processed_bucket_name = var.processed_bucket_name

  # Lambda
  lambda_function_name = var.lambda_function_name
  lambda_runtime       = var.lambda_runtime
  lambda_handler       = var.lambda_handler

  # Glue
  glue_job_name = var.glue_job_name
  glue_role_name = var.glue_role_name
}

# GCP Resources
module "gcp_infrastructure" {
  source = "./gcp"

  # Vertex AI
  vertex_ai_model_name = var.vertex_ai_model_name
  vertex_ai_endpoint_name = var.vertex_ai_endpoint_name
  vertex_ai_machine_type = var.vertex_ai_machine_type
}

# Outputs
output "kinesis_stream_arn" {
  value = module.aws_infrastructure.kinesis_stream_arn
}

output "s3_raw_bucket_name" {
  value = module.aws_infrastructure.raw_bucket_name
}

output "s3_processed_bucket_name" {
  value = module.aws_infrastructure.processed_bucket_name
}

output "vertex_ai_endpoint_id" {
  value = module.gcp_infrastructure.vertex_ai_endpoint_id
} 