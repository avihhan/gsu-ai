# Syllabus Document Processing System

A comprehensive backend system for processing and analyzing syllabus documents using AWS services. The system supports document upload, text extraction, embedding generation, and semantic search capabilities.

## Features

- **Document Upload**: Accept PDF, DOC, and DOCX files with user tracking
- **Text Extraction**: Convert documents to structured JSON format
- **Embedding Generation**: Create vector embeddings using AWS Bedrock
- **Semantic Search**: Query documents using vector similarity search
- **User Management**: Track document ownership and access
- **Scalable Architecture**: Built on AWS services for high availability

## Architecture

### AWS Services Used

- **Amazon S3**: Document storage and file management
- **Amazon RDS PostgreSQL**: Relational database for metadata
- **Amazon OpenSearch Service**: Vector database for embeddings
- **AWS Bedrock**: AI/ML service for embedding generation
- **AWS Lambda** (optional): Serverless processing functions
- **AWS CloudWatch**: Monitoring and logging

### Service Mapping

| Azure Service | AWS Equivalent | Purpose |
|---------------|----------------|---------|
| Azure Blob Storage | Amazon S3 | Document storage |
| Azure PostgreSQL | Amazon RDS PostgreSQL | Metadata storage |
| Azure Cosmos DB | Amazon OpenSearch Service | Vector database |
| Azure OpenAI | AWS Bedrock | Embedding generation |
| Azure Functions | AWS Lambda | Serverless processing |
| Azure App Service | AWS App Runner | Application hosting |

## Prerequisites

- AWS Account with appropriate permissions
- Python 3.8+
- Docker and Docker Compose
- AWS CLI configured

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd syllabus-processing-system
```

### 2. Set Up Environment Variables

Copy the example environment file and configure your AWS credentials:

```bash
cp env.example .env
```

Edit `.env` with your AWS configuration:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-syllabus-bucket

# RDS Configuration
RDS_HOST=your-rds-endpoint.region.rds.amazonaws.com
RDS_DB=syllabus_db
RDS_USER=your_username
RDS_PASSWORD=your_password

# OpenSearch Configuration
OPENSEARCH_ENDPOINT=https://your-opensearch-domain.region.es.amazonaws.com
OPENSEARCH_USERNAME=your_username
OPENSEARCH_PASSWORD=your_password

# Bedrock Configuration
BEDROCK_MODEL_ID=amazon.titan-embed-text-v1
```

### 3. Run with Docker Compose

```bash
# Start the application
docker-compose up -d

# For local development with PostgreSQL
docker-compose --profile local-dev up -d
```

### 4. Run Locally (Alternative)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python document_upload.py
```

## Usage Examples

### Upload a Document

```python
from document_upload import upload_syllabus_document

# Upload a syllabus document
result = upload_syllabus_document(
    file_path="path/to/syllabus.pdf",
    user_id="user123"
)

if result['success']:
    print(f"Document uploaded successfully!")
    print(f"Document ID: {result['document_id']}")
    print(f"S3 URL: {result['s3_url']}")
else:
    print(f"Upload failed: {result['error']}")
```

### Using the DocumentUploader Class

```python
from document_upload import DocumentUploader

# Initialize uploader
uploader = DocumentUploader(
    aws_access_key_id="your_key",
    aws_secret_access_key="your_secret",
    aws_region="us-east-1",
    s3_bucket_name="your-bucket"
)

# Upload document
result = uploader.upload_document(
    file_path="syllabus.pdf",
    user_id="user123"
)
```

## Database Schema

### Tables

- **users**: User information and authentication
- **documents**: Document metadata and storage information
- **document_processing**: Processing status and history
- **embeddings**: Vector embeddings for semantic search

### Key Relationships

- Documents belong to users (user_id foreign key)
- Embeddings belong to documents (document_id foreign key)
- Processing records track document processing status

## API Endpoints (Future)

The system is designed to support RESTful API endpoints:

- `POST /api/documents/upload` - Upload a new document
- `GET /api/documents/{id}` - Get document information
- `POST /api/documents/{id}/process` - Trigger document processing
- `GET /api/documents/{id}/embeddings` - Get document embeddings
- `POST /api/search` - Search documents by query
- `GET /api/users/{id}/documents` - Get user's documents

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | us-east-1 |
| `S3_BUCKET_NAME` | S3 bucket for documents | syllabus-documents |
| `RDS_HOST` | RDS PostgreSQL endpoint | Required |
| `RDS_DB` | Database name | syllabus_db |
| `RDS_USER` | Database username | Required |
| `RDS_PASSWORD` | Database password | Required |
| `OPENSEARCH_ENDPOINT` | OpenSearch endpoint | Required |
| `BEDROCK_MODEL_ID` | Bedrock model for embeddings | amazon.titan-embed-text-v1 |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 52428800 (50MB) |
| `SUPPORTED_EXTENSIONS` | Supported file extensions | .pdf,.doc,.docx |

### File Size Limits

- Default maximum file size: 50MB
- Supported formats: PDF, DOC, DOCX
- Configurable via `MAX_FILE_SIZE` environment variable

## Security

### AWS IAM Permissions

The application requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*:*:foundation-model/amazon.titan-embed-text-v1"
        }
    ]
}
```

### Security Best Practices

- Use IAM roles instead of access keys when possible
- Enable S3 bucket encryption
- Use RDS encryption at rest
- Implement proper network security groups
- Enable CloudWatch logging and monitoring

## Development

### Project Structure

```
syllabus-processing-system/
├── document_upload.py      # Main upload functionality
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-service orchestration
├── init.sql             # Database initialization
├── env.example          # Environment variables template
├── .gitignore          # Git ignore rules
├── notes.txt           # Architecture notes
└── README.md           # This file
```

### Adding New Features

1. **New Document Types**: Update `SUPPORTED_EXTENSIONS` in config
2. **Custom Processing**: Extend `DocumentUploader` class
3. **Additional Metadata**: Modify database schema in `init.sql`
4. **New Search Features**: Implement in OpenSearch queries

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Test document upload
python document_upload.py
```

## Deployment

### AWS Deployment Options

#### Option 1: AWS App Runner
```bash
# Build and push to ECR
docker build -t syllabus-processor .
docker tag syllabus-processor:latest your-account.dkr.ecr.region.amazonaws.com/syllabus-processor:latest
docker push your-account.dkr.ecr.region.amazonaws.com/syllabus-processor:latest

# Deploy to App Runner
aws apprunner create-service --cli-input-json apprunner-config.json
```

#### Option 2: AWS ECS/Fargate
```bash
# Deploy using ECS
aws ecs create-cluster --cluster-name syllabus-cluster
aws ecs register-task-definition --cli-input-json task-definition.json
aws ecs create-service --cli-input-json service-definition.json
```

#### Option 3: AWS Lambda
```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cd package && zip -r ../lambda-deployment.zip .
```

### Infrastructure as Code

Consider using AWS CDK or Terraform for infrastructure management:

```python
# Example CDK stack
from aws_cdk import (
    aws_s3 as s3,
    aws_rds as rds,
    aws_opensearchservice as opensearch
)

class SyllabusStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # S3 Bucket
        bucket = s3.Bucket(self, "SyllabusBucket")
        
        # RDS Instance
        database = rds.DatabaseInstance(self, "SyllabusDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15)
        )
        
        # OpenSearch Domain
        opensearch_domain = opensearch.Domain(self, "SyllabusOpenSearch",
            version=opensearch.EngineVersion.OPENSEARCH_2_5
        )
```

## Monitoring and Logging

### CloudWatch Integration

- Application logs are sent to CloudWatch
- Metrics for upload success/failure rates
- Alerts for system health and performance

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
python -c "from config import config; print(config.get_database_url())"
```

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Ensure AWS credentials are properly configured
2. **S3 Permissions**: Verify S3 bucket permissions and CORS settings
3. **RDS Connectivity**: Check security groups and network access
4. **OpenSearch Access**: Verify OpenSearch domain access policies

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python document_upload.py
```

### Error Handling

The system includes comprehensive error handling:
- File validation errors
- AWS service errors
- Database connection errors
- Processing pipeline errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review AWS documentation for service-specific issues

## Roadmap

- [ ] REST API implementation
- [ ] Web interface for document management
- [ ] Advanced search features
- [ ] Document versioning
- [ ] Multi-tenant support
- [ ] Performance optimizations
- [ ] Additional document formats
- [ ] Real-time processing notifications
