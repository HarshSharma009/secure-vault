import os
import hashlib
import logging
import traceback
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import File
from .repositories import FileRepository

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.repository = FileRepository()

    def calculate_file_hash(self, file_content):
        """Calculate SHA-256 hash of file content."""
        try:
            logger.debug("Calculating file hash")
            return hashlib.sha256(file_content).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def get_file_extension(self, filename):
        """Get file extension from filename."""
        try:
            logger.debug(f"Getting file extension for: {filename}")
            return os.path.splitext(filename)[1].lower()
        except Exception as e:
            logger.error(f"Error getting file extension: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def save_file(self, file_obj, original_filename):
        """Save file and create database record."""
        try:
            logger.info(f"Starting file save process for: {original_filename}")
            
            # Read file content
            logger.debug("Reading file content")
            file_content = file_obj.read()
            
            # Calculate file hash
            logger.debug("Calculating file hash")
            file_hash = self.calculate_file_hash(file_content)
            logger.debug(f"File hash: {file_hash}")
            
            # Check for duplicate
            logger.debug("Checking for duplicate file")
            existing_file = self.repository.get_file_by_hash(file_hash)
            if existing_file:
                logger.info(f"Duplicate file found: {existing_file.original_filename}")
                return existing_file, True
            
            # Get file extension
            logger.debug("Getting file extension")
            file_extension = self.get_file_extension(original_filename)
            
            # Generate unique filename
            unique_filename = f"{file_hash}{file_extension}"
            logger.debug(f"Generated unique filename: {unique_filename}")
            
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Save file to storage
            logger.debug("Saving file to storage")
            file_path = os.path.join('uploads', unique_filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Write file content
            with open(full_path, 'wb') as f:
                f.write(file_content)
            
            logger.debug(f"File saved to: {file_path}")
            
            # Create database record
            logger.debug("Creating database record")
            file_obj = File.objects.create(
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_extension[1:],  # Remove the dot
                size=len(file_content),
                file_hash=file_hash,
                is_duplicate=False
            )
            logger.info(f"File saved successfully: {original_filename}")
            
            return file_obj, False
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Clean up any partially saved files
            if 'full_path' in locals() and os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up file: {str(cleanup_error)}")
            raise

    def search_files(self, filters):
        """Search files with filters."""
        return self.repository.search_files(filters)

    def get_storage_stats(self):
        """Get storage statistics."""
        try:
            logger.debug("Getting storage stats from repository")
            stats = self.repository.get_storage_stats()
            logger.debug(f"Retrieved storage stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error in get_storage_stats service: {str(e)}")
            raise

    def delete_file(self, file_id):
        """Delete file and its record."""
        try:
            file_obj = File.objects.get(id=file_id)
            
            # Only delete the actual file if it's not a duplicate
            if not file_obj.is_duplicate:
                default_storage.delete(file_obj.file_path)
            
            file_obj.delete()
            return True
        except File.DoesNotExist:
            return False 