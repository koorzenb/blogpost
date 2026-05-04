"""
Database configuration for AWS Aurora PostgreSQL with IAM authentication
"""
import os
import boto3
from dotenv import load_dotenv

load_dotenv('.env.local')

def get_database_uri():
    """
    Generate a PostgreSQL connection URI with IAM authentication token.
    The token is valid for 15 minutes.
    """
    # Get database connection details from environment
    host = os.environ.get('PGHOST')
    port = os.environ.get('PGPORT', '5432')
    database = os.environ.get('PGDATABASE', 'postgres')
    user = os.environ.get('PGUSER')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # For local development without AWS credentials, 
    # fall back to a regular connection string if available
    if 'DB_PASSWORD' in os.environ:
        password = os.environ.get('DB_PASSWORD')
        return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
    
    # Generate IAM authentication token
    try:
        client = boto3.client('rds', region_name=region)
        token = client.generate_db_auth_token(
            DBHostname=host,
            Port=int(port),
            DBUsername=user,
            Region=region
        )
        
        # Construct the connection string with the token as password
        return f"postgresql://{user}:{token}@{host}:{port}/{database}?sslmode=require"
    
    except Exception as e:
        print(f"Error generating IAM token: {e}")
        # Fallback to SQLite for local development
        return "sqlite:///posts.db"
