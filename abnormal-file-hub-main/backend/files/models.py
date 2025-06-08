from django.db import models
import uuid
import os
import hashlib
from django.utils import timezone

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

def calculate_file_hash(file_obj):
    """Calculate SHA-256 hash of file content"""
    sha256_hash = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, unique=True)
    is_duplicate = models.BooleanField(default=False)
    original_file = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='duplicates')
    reference_count = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['file_type']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['size']),
        ]
    
    def __str__(self):
        return self.original_filename

    def get_file_path(self):
        """Get the full file path."""
        return os.path.join('media', self.file_path)

    def delete(self, *args, **kwargs):
        """Delete the file from storage when the model is deleted."""
        try:
            # Only delete the actual file if it's not a duplicate
            if not self.is_duplicate:
                full_path = os.path.join('media', self.file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        except Exception as e:
            # Log the error but continue with model deletion
            print(f"Error deleting file: {str(e)}")
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.file_hash and self.file:
            self.file_hash = calculate_file_hash(self.file)
        super().save(*args, **kwargs)
