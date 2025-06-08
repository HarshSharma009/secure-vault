from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    original_file_details = serializers.SerializerMethodField()
    duplicates_count = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'id', 'file', 'original_filename', 'file_type', 'size',
            'uploaded_at', 'is_duplicate', 'original_file', 'original_file_details',
            'reference_count', 'duplicates_count'
        ]
        read_only_fields = ['id', 'uploaded_at', 'is_duplicate', 'reference_count']

    def get_original_file_details(self, obj):
        if obj.original_file:
            return {
                'id': obj.original_file.id,
                'original_filename': obj.original_file.original_filename,
                'file_type': obj.original_file.file_type,
                'size': obj.original_file.size,
                'uploaded_at': obj.original_file.uploaded_at
            }
        return None

    def get_duplicates_count(self, obj):
        if not obj.is_duplicate:
            return File.objects.filter(original_file=obj).count()
        return 0 