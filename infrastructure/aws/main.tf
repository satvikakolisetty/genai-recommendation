# Kinesis Stream
resource "aws_kinesis_stream" "recommendation_events" {
  name             = var.kinesis_stream_name
  shard_count      = var.shard_count
  retention_period = 24

  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

# S3 Buckets
resource "aws_s3_bucket" "raw_data" {
  bucket = var.raw_bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "processed_data" {
  bucket = var.processed_bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

# IAM Roles
resource "aws_iam_role" "lambda_role" {
  name = "recommendation-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "recommendation-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListShards"
        ]
        Resource = aws_kinesis_stream.recommendation_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.raw_data.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "kinesis_processor" {
  filename         = "${path.module}/lambda_function.zip"
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = var.lambda_handler
  runtime          = var.lambda_runtime
  timeout          = 300
  memory_size      = 512

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.raw_data.id
    }
  }
}

# Lambda Event Source Mapping
resource "aws_lambda_event_source_mapping" "kinesis_to_lambda" {
  event_source_arn  = aws_kinesis_stream.recommendation_events.arn
  function_name     = aws_lambda_function.kinesis_processor.arn
  starting_position = "LATEST"
  batch_size        = 100
}

# Glue Role
resource "aws_iam_role" "glue_role" {
  name = var.glue_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "glue_policy" {
  name = "recommendation-glue-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.processed_data.arn}/*",
          aws_s3_bucket.processed_data.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Glue Job
resource "aws_glue_job" "recommendation_etl" {
  name         = var.glue_job_name
  role_arn     = aws_iam_role.glue_role.arn
  max_retries  = 0
  timeout      = 2880
  worker_type  = "G.1X"
  number_of_workers = 10

  command {
    script_location = "s3://${aws_s3_bucket.processed_data.id}/scripts/etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"
    "--TempDir"     = "s3://${aws_s3_bucket.processed_data.id}/temp/"
    "--job-bookmark-option" = "job-bookmark-enable"
    "--enable-metrics" = "true"
  }
}

# Glue Trigger
resource "aws_glue_trigger" "recommendation_trigger" {
  name     = "recommendation-trigger"
  type     = "SCHEDULED"
  schedule = "cron(0 * * * ? *)"

  actions {
    job_name = aws_glue_job.recommendation_etl.name
  }
}

# Outputs
output "kinesis_stream_arn" {
  value = aws_kinesis_stream.recommendation_events.arn
}

output "raw_bucket_name" {
  value = aws_s3_bucket.raw_data.id
}

output "processed_bucket_name" {
  value = aws_s3_bucket.processed_data.id
} 