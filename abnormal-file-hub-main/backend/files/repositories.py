from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import File
import logging

logger = logging.getLogger(__name__)

class FileRepository:
    @staticmethod
    def get_all_files():
        return File.objects.all()

    @staticmethod
    def get_file_by_hash(file_hash):
        return File.objects.filter(file_hash=file_hash).first()

    @staticmethod
    def search_files(filters):
        query = Q()
        
        # Search by filename
        filename = filters.get('filename', '')
        if filename:
            query &= Q(original_filename__icontains=filename)
        
        # Filter by file type
        file_type = filters.get('file_type', '')
        if file_type:
            query &= Q(file_type__icontains=file_type)
        
        # Filter by size range
        min_size = filters.get('min_size')
        max_size = filters.get('max_size')
        if min_size:
            query &= Q(size__gte=min_size)
        if max_size:
            query &= Q(size__lte=max_size)
        
        # Filter by upload date
        date_range = filters.get('date_range', '')
        if date_range:
            today = timezone.now()
            if date_range == 'today':
                query &= Q(uploaded_at__date=today.date())
            elif date_range == 'week':
                query &= Q(uploaded_at__gte=today - timedelta(days=7))
            elif date_range == 'month':
                query &= Q(uploaded_at__gte=today - timedelta(days=30))
        
        return File.objects.filter(query)

    @staticmethod
    def get_storage_stats():
        try:
            # Get total size of unique files
            total_size = File.objects.filter(is_duplicate=False).aggregate(Sum('size'))['size__sum'] or 0
            logger.debug(f"Total size of unique files: {total_size}")
            
            # Get total size of all files
            original_size = File.objects.aggregate(Sum('size'))['size__sum'] or 0
            logger.debug(f"Total size of all files: {original_size}")
            
            # Calculate savings
            savings = original_size - total_size
            logger.debug(f"Storage savings: {savings}")
            
            # Get file counts
            total_files = File.objects.count()
            unique_files = File.objects.filter(is_duplicate=False).count()
            duplicate_files = File.objects.filter(is_duplicate=True).count()
            
            logger.debug(f"Total files: {total_files}")
            logger.debug(f"Unique files: {unique_files}")
            logger.debug(f"Duplicate files: {duplicate_files}")
            
            return {
                'total_files': total_files,
                'unique_files': unique_files,
                'duplicate_files': duplicate_files,
                'total_size_bytes': original_size,
                'unique_size_bytes': total_size,
                'storage_savings_bytes': savings,
                'storage_savings_percentage': (savings / original_size * 100) if original_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating storage stats: {str(e)}")
            raise 