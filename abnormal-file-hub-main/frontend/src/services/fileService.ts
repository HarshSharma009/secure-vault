import axios from 'axios';
import { File as FileType } from '../types/file';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export interface SearchFilters {
  filename?: string;
  fileType?: string;
  minSize?: number;
  maxSize?: number;
  dateRange?: 'today' | 'week' | 'month';
}

export interface StorageStats {
  total_files: number;
  unique_files: number;
  duplicate_files: number;
  total_size_bytes: number;
  unique_size_bytes: number;
  storage_savings_bytes: number;
  storage_savings_percentage: number;
}

export const fileService = {
  async uploadFile(file: File): Promise<FileType> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/files/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 409) {
        // Pass through the error response from the backend
        throw error;
      }
      throw error;
    }
  },

  async getFiles(): Promise<FileType[]> {
    const response = await axios.get(`${API_URL}/files/`);
    return response.data;
  },

  async searchFiles(filters: SearchFilters): Promise<FileType[]> {
    const params = new URLSearchParams();
    
    if (filters.filename) params.append('filename', filters.filename);
    if (filters.fileType) params.append('file_type', filters.fileType);
    if (filters.minSize) params.append('min_size', filters.minSize.toString());
    if (filters.maxSize) params.append('max_size', filters.maxSize.toString());
    if (filters.dateRange) params.append('date_range', filters.dateRange);

    const response = await axios.get(`${API_URL}/files/search/`, { params });
    return response.data;
  },

  async getStorageStats(): Promise<StorageStats> {
    const response = await axios.get(`${API_URL}/files/stats/`);
    return response.data;
  },

  async deleteFile(id: string): Promise<void> {
    await axios.delete(`${API_URL}/files/${id}/`);
  },

  async downloadFile(id: string, filename: string): Promise<void> {
    if (!id) {
      throw new Error('Invalid file ID');
    }

    try {
      const response = await axios.get(`${API_URL}/files/${id}/`, {
        responseType: 'blob',
      });
      
      // Create a blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Download error:', error);
      if (error.response?.status === 404) {
        throw new Error('File not found');
      } else if (error.response?.status === 500) {
        throw new Error(error.response.data?.detail || 'Server error while downloading file');
      } else {
        throw new Error('Failed to download file');
      }
    }
  },
}; 