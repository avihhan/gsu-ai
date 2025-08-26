import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import mimetypes
import logging

# AWS SDK imports (you'll need to install these)
import boto3
from botocore.exceptions import ClientError
import psycopg2
from psycopg2.extras import RealDictCursor

# Import configuration
from config import config

class DocumentUploader:
    """
    Handles document upload functionality for syllabus documents using AWS services.
    Supports PDF, DOC, and DOCX formats.
    """
    
    def __init__(self, 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_region: Optional[str] = None,
                 s3_bucket_name: Optional[str] = None,
                 db_connection_string: Optional[str] = None):
        """
        Initialize the document uploader.
        
        Args:
            aws_access_key_id: AWS access key ID (optional, uses config if not provided)
            aws_secret_access_key: AWS secret access key (optional, uses config if not provided)
            aws_region: AWS region (optional, uses config if not provided)
            s3_bucket_name: Name of the S3 bucket (optional, uses config if not provided)
            db_connection_string: PostgreSQL database connection string (optional, uses config if not provided)
        """
        # Use provided values or fall back to config
        self.aws_access_key_id = aws_access_key_id or config.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key or config.AWS_SECRET_ACCESS_KEY
        self.aws_region = aws_region or config.AWS_REGION
        self.s3_bucket_name = s3_bucket_name or config.S3_BUCKET_NAME
        self.db_connection_string = db_connection_string or config.get_database_url()
        
        # Validate configuration
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.aws_region]):
            raise ValueError("AWS credentials and region are required")
        if not self.db_connection_string:
            raise ValueError("Database connection string is required")
        
        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        
        # Supported file extensions from config
        self.supported_extensions = set(config.SUPPORTED_EXTENSIONS)
        
        # Set up logging
        logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
        self.logger = logging.getLogger(__name__)
        
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate uploaded file format and size.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dict containing validation results and file info
        """
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }
            
            # Check file extension
            file_extension = file_path.suffix.lower()
            if file_extension not in self.supported_extensions:
                return {
                    'valid': False,
                    'error': f'Unsupported file format. Supported formats: {", ".join(self.supported_extensions)}'
                }
            
            # Check file size (from config)
            file_size = file_path.stat().st_size
            max_size = config.MAX_FILE_SIZE
            if file_size > max_size:
                return {
                    'valid': False,
                    'error': f'File too large. Maximum size: {max_size / (1024*1024):.0f}MB, Current size: {file_size / (1024*1024):.2f}MB'
                }
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                'valid': True,
                'file_name': file_path.name,
                'file_extension': file_extension,
                'file_size': file_size,
                'mime_type': mime_type,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def upload_to_s3(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Upload file to Amazon S3.
        
        Args:
            file_path: Local path to the file
            file_name: Name to use for the file in S3
            
        Returns:
            Dict containing upload results and S3 URL
        """
        try:
            # Upload file to S3
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket_name,
                file_name
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.s3_bucket_name}.s3.{self.aws_region}.amazonaws.com/{file_name}"
            
            return {
                'success': True,
                's3_url': s3_url,
                's3_key': file_name
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'S3 upload error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload error: {str(e)}'
            }
    
    def save_to_database(self, file_metadata: Dict[str, Any], s3_url: str, user_id: str) -> Dict[str, Any]:
        """
        Save file metadata to PostgreSQL database.
        
        Args:
            file_metadata: File validation metadata
            s3_url: URL of the uploaded file in S3
            user_id: ID of the user who uploaded the document
            
        Returns:
            Dict containing database operation results
        """
        try:
            # Connect to database
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Insert document metadata
            insert_query = """
                INSERT INTO documents (
                    document_id, 
                    user_id,
                    file_name, 
                    file_extension, 
                    file_size, 
                    mime_type, 
                    s3_url, 
                    upload_date, 
                    status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING document_id
            """
            
            cursor.execute(insert_query, (
                document_id,
                user_id,
                file_metadata['file_name'],
                file_metadata['file_extension'],
                file_metadata['file_size'],
                file_metadata['mime_type'],
                s3_url,
                datetime.utcnow(),
                'uploaded'
            ))
            
            # Commit transaction
            conn.commit()
            
            # Get inserted record
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'document_id': result['document_id'],
                'message': 'Document metadata saved successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def upload_document(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Main function to upload a syllabus document.
        
        Args:
            file_path: Path to the document file
            user_id: ID of the user who uploaded the document
            
        Returns:
            Dict containing upload results
        """
        try:
            # Step 1: Validate file
            validation_result = self.validate_file(file_path)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Step 2: Generate unique S3 key
            file_extension = validation_result['file_extension']
            unique_name = f"{uuid.uuid4()}{file_extension}"
            
            # Step 3: Upload to S3
            upload_result = self.upload_to_s3(file_path, unique_name)
            if not upload_result['success']:
                return {
                    'success': False,
                    'error': upload_result['error']
                }
            
            # Step 4: Save metadata to database
            db_result = self.save_to_database(validation_result, upload_result['s3_url'], user_id)
            if not db_result['success']:
                return {
                    'success': False,
                    'error': db_result['error']
                }
            
            return {
                'success': True,
                'document_id': db_result['document_id'],
                'file_name': validation_result['file_name'],
                's3_url': upload_result['s3_url'],
                'message': 'Document uploaded successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }

# Example usage function
def upload_syllabus_document(file_path: str, 
                           user_id: str,
                           aws_access_key_id: Optional[str] = None,
                           aws_secret_access_key: Optional[str] = None,
                           aws_region: Optional[str] = None,
                           s3_bucket_name: Optional[str] = None,
                           db_connection_string: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to upload a syllabus document.
    
    Args:
        file_path: Path to the document file
        user_id: ID of the user who uploaded the document
        aws_access_key_id: AWS access key ID (optional, uses config if not provided)
        aws_secret_access_key: AWS secret access key (optional, uses config if not provided)
        aws_region: AWS region (optional, uses config if not provided)
        s3_bucket_name: Name of the S3 bucket (optional, uses config if not provided)
        db_connection_string: PostgreSQL database connection string (optional, uses config if not provided)
        
    Returns:
        Dict containing upload results
    """
    uploader = DocumentUploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
        s3_bucket_name=s3_bucket_name,
        db_connection_string=db_connection_string
    )
    
    return uploader.upload_document(file_path, user_id)

# Example usage
if __name__ == "__main__":
    try:
        # Validate configuration
        config.validate_config()
        
        # Example upload using environment variables
        result = upload_syllabus_document(
            file_path="path/to/your/syllabus.pdf",
            user_id="user123"  # Replace with actual user ID
        )
        
        if result['success']:
            print(f"Upload successful! Document ID: {result['document_id']}")
            print(f"File: {result['file_name']}")
            print(f"S3 URL: {result['s3_url']}")
        else:
            print(f"Upload failed: {result['error']}")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
