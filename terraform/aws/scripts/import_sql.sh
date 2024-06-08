#!/bin/bash

# Variables
S3_BUCKET="ce-bucket-prod"
SQL_FILE="Cloud_SQL_Export.sql"
DB_HOST="ce-aurora-cluster.cluster-cb2u6sse4azd.us-east-1.rds.amazonaws.com"
DB_USER="postgres"
DB_NAME="production"

# Download the SQL file from S3
aws s3 cp "s3://$S3_BUCKET/$SQL_FILE" .

# Import the SQL file into PostgreSQL
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f "$SQL_FILE"