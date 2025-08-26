import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the syllabus processing system using AWS services."""
    
    # AWS S3 Configuration (replaces Azure Blob Storage)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'syllabus-documents')
    
    # Amazon RDS PostgreSQL Configuration (replaces Azure PostgreSQL)
    RDS_HOST = os.getenv('RDS_HOST')
    RDS_PORT = int(os.getenv('RDS_PORT', '5432'))
    RDS_DB = os.getenv('RDS_DB')
    RDS_USER = os.getenv('RDS_USER')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD')
    RDS_SSL_MODE = os.getenv('RDS_SSL_MODE', 'require')
    
    # Amazon OpenSearch Service Configuration (replaces Azure Cosmos DB)
    OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
    OPENSEARCH_USERNAME = os.getenv('OPENSEARCH_USERNAME')
    OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD')
    OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX', 'embeddings')
    
    # AWS Bedrock Configuration (replaces Azure OpenAI)
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-embed-text-v1')
    BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-east-1')
    
    # Application Configuration
    APP_ENV = os.getenv('APP_ENV', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '52428800'))  # 50MB default
    SUPPORTED_EXTENSIONS = os.getenv('SUPPORTED_EXTENSIONS', '.pdf,.doc,.docx').split(',')
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Generate PostgreSQL connection string from environment variables."""
        if not all([cls.RDS_HOST, cls.RDS_DB, cls.RDS_USER, cls.RDS_PASSWORD]):
            raise ValueError("Missing required RDS PostgreSQL environment variables")
        
        return f"postgresql://{cls.RDS_USER}:{cls.RDS_PASSWORD}@{cls.RDS_HOST}:{cls.RDS_PORT}/{cls.RDS_DB}?sslmode={cls.RDS_SSL_MODE}"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration variables are set."""
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_REGION',
            'S3_BUCKET_NAME',
            'RDS_HOST',
            'RDS_DB',
            'RDS_USER',
            'RDS_PASSWORD',
            'OPENSEARCH_ENDPOINT',
            'OPENSEARCH_USERNAME',
            'OPENSEARCH_PASSWORD',
            'BEDROCK_MODEL_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.APP_ENV.lower() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.APP_ENV.lower() == 'development'

# Create a global config instance
config = Config()
