import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *
import boto3
import json

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'raw_bucket', 'processed_bucket'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read raw data from S3
raw_data = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [f"s3://{args['raw_bucket']}/raw/"],
        "recurse": True
    },
    format="json"
)

# Convert to DataFrame for processing
df = raw_data.toDF()

# Define schema for user interactions
interaction_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("item_id", StringType(), True),
    StructField("interaction_type", StringType(), True),
    StructField("event_time", TimestampType(), True),
    StructField("processed_at", TimestampType(), True),
    StructField("metadata", MapType(StringType(), StringType()), True)
])

# Transform and clean data
processed_df = df.select(
    col("user_id").cast("string"),
    col("item_id").cast("string"),
    col("interaction_type").cast("string"),
    to_timestamp(col("event_time")).alias("event_time"),
    to_timestamp(col("processed_at")).alias("processed_at"),
    col("metadata")
).filter(
    col("user_id").isNotNull() &
    col("item_id").isNotNull() &
    col("interaction_type").isNotNull() &
    col("event_time").isNotNull()
)

# Write processed data to S3
processed_df.write.partitionBy("event_time").parquet(
    f"s3://{args['processed_bucket']}/processed/",
    mode="append"
)

# Snowflake connection parameters
sf_options = {
    "sfURL": "your-account.snowflakecomputing.com",
    "sfUser": "your-user",
    "sfPassword": "your-password",
    "sfDatabase": "RECOMMENDATION_DB",
    "sfSchema": "PUBLIC",
    "sfWarehouse": "RECOMMENDATION_WH"
}

# Write to Snowflake
processed_df.write.format("snowflake") \
    .options(**sf_options) \
    .option("dbtable", "USER_INTERACTIONS") \
    .mode("append") \
    .save()

job.commit() 