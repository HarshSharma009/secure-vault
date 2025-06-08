from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import File
from .serializers import FileSerializer

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['original_filename', 'file_type']
    ordering_fields = ['uploaded_at', 'size', 'file_type']
    ordering = ['-uploaded_at']

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate file hash
        file_hash = self.calculate_file_hash(file_obj)
        
        # Check for duplicate
        existing_file = File.objects.filter(file_hash=file_hash).first()
        if existing_file:
            # Create a duplicate reference
            duplicate = File(
                original_filename=file_obj.name,
                file_type=file_obj.content_type,
                size=file_obj.size,
                file_hash=file_hash,
                is_duplicate=True,
                original_file=existing_file
            )
            duplicate.save()
            existing_file.reference_count += 1
            existing_file.save()
            
            serializer = self.get_serializer(duplicate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If no duplicate found, create new file
        data = {
            'file': file_obj,
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size,
            'file_hash': file_hash
        }
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def calculate_file_hash(self, file_obj):
        """Calculate SHA-256 hash of file content"""
        import hashlib
        sha256_hash = hashlib.sha256()
        for chunk in file_obj.chunks():
            sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Enhanced search with multiple filters"""
        query = Q()
        
        # Search by filename
        filename = request.query_params.get('filename', '')
        if filename:
            query &= Q(original_filename__icontains=filename)
        
        # Filter by file type
        file_type = request.query_params.get('file_type', '')
        if file_type:
            query &= Q(file_type__icontains=file_type)
        
        # Filter by size range
        min_size = request.query_params.get('min_size')
        max_size = request.query_params.get('max_size')
        if min_size:
            query &= Q(size__gte=min_size)
        if max_size:
            query &= Q(size__lte=max_size)
        
        # Filter by upload date
        date_range = request.query_params.get('date_range', '')
        if date_range:
            today = timezone.now()
            if date_range == 'today':
                query &= Q(uploaded_at__date=today.date())
            elif date_range == 'week':
                query &= Q(uploaded_at__gte=today - timedelta(days=7))
            elif date_range == 'month':
                query &= Q(uploaded_at__gte=today - timedelta(days=30))
        
        files = File.objects.filter(query)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def storage_stats(self, request):
        """Get storage statistics including deduplication savings"""
        total_size = File.objects.filter(is_duplicate=False).aggregate(Sum('size'))['size__sum'] or 0
        original_size = File.objects.aggregate(Sum('size'))['size__sum'] or 0
        savings = original_size - total_size
        
        stats = {
            'total_files': File.objects.count(),
            'unique_files': File.objects.filter(is_duplicate=False).count(),
            'duplicate_files': File.objects.filter(is_duplicate=True).count(),
            'total_size_bytes': original_size,
            'unique_size_bytes': total_size,
            'storage_savings_bytes': savings,
            'storage_savings_percentage': (savings / original_size * 100) if original_size > 0 else 0
        }
        
        return Response(stats)
