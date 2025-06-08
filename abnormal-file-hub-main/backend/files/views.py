from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import File
from .serializers import FileSerializer
from .services import FileService
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from django.core.files.storage import default_storage
import logging
import traceback
import os
from django.conf import settings

# Create your views here.

logger = logging.getLogger(__name__)

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['original_filename', 'file_type']
    ordering_fields = ['uploaded_at', 'size', 'file_type']
    ordering = ['-uploaded_at']
    parser_classes = (MultiPartParser, FormParser)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_service = FileService()

    def create(self, request, *args, **kwargs):
        logger.info("Starting file upload process")
        try:
            if 'file' not in request.FILES:
                logger.error("No file provided in request")
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            file_obj = request.FILES['file']
            original_filename = file_obj.name
            logger.info(f"Processing file: {original_filename}")

            try:
                file_obj, is_duplicate = self.file_service.save_file(file_obj, original_filename)
                logger.info(f"File processed successfully. Duplicate: {is_duplicate}")
                
                if is_duplicate:
                    logger.info(f"Duplicate file detected: {original_filename}")
                    return Response(
                        {
                            'error': 'Duplicate file detected',
                            'existing_file': {
                                'id': file_obj.id,
                                'filename': file_obj.original_filename,
                                'uploaded_at': file_obj.uploaded_at,
                                'size': file_obj.size
                            }
                        },
                        status=status.HTTP_409_CONFLICT
                    )
                
                serializer = self.get_serializer(file_obj)
                logger.info(f"File uploaded successfully: {original_filename}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return Response(
                    {
                        'error': 'Error processing file',
                        'detail': str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in file upload: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {
                    'error': 'Unexpected error during file upload',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            logger.info("Starting file download process")
            file_obj = self.get_object()
            file_path = file_obj.file_path
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            logger.debug(f"Attempting to download file: {file_path}")
            
            if not os.path.exists(full_path):
                logger.error(f"File not found at path: {full_path}")
                return Response(
                    {'error': 'File not found in storage'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                file = open(full_path, 'rb')
                response = FileResponse(file)
                response['Content-Disposition'] = f'attachment; filename="{file_obj.original_filename}"'
                response['Content-Type'] = 'application/octet-stream'
                logger.info(f"File download successful: {file_obj.original_filename}")
                return response
            except Exception as e:
                logger.error(f"Error opening file: {str(e)}")
                return Response(
                    {'error': 'Error reading file'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except File.DoesNotExist:
            logger.error("File record not found in database")
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error in file download: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {
                    'error': 'Failed to download file',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        try:
            filters = {
                'filename': request.query_params.get('filename', ''),
                'file_type': request.query_params.get('file_type', ''),
                'min_size': request.query_params.get('min_size'),
                'max_size': request.query_params.get('max_size'),
                'date_range': request.query_params.get('date_range', '')
            }
            
            files = self.file_service.search_files(filters)
            serializer = self.get_serializer(files, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            logger.debug("Processing stats request")
            stats = self.file_service.get_storage_stats()
            logger.debug(f"Successfully retrieved stats: {stats}")
            return Response(stats)
        except Exception as e:
            logger.error(f"Error in stats view: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve storage statistics',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            file_id = kwargs.get('pk')
            if self.file_service.delete_file(file_id):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
