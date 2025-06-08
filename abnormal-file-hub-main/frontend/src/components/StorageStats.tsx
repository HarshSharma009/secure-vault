import React from 'react';
import { StorageStats as StorageStatsType } from '../services/fileService';

interface StorageStatsProps {
  stats: StorageStatsType;
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const StorageStats: React.FC<StorageStatsProps> = ({ stats }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <h2 className="text-lg font-semibold mb-4">Storage Statistics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Total Files</h3>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{stats.total_files}</p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Unique Files</h3>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{stats.unique_files}</p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Duplicate Files</h3>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{stats.duplicate_files}</p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Total Storage</h3>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{formatBytes(stats.total_size_bytes)}</p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Unique Storage</h3>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{formatBytes(stats.unique_size_bytes)}</p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-500">Storage Savings</h3>
          <p className="mt-1 text-2xl font-semibold text-green-600">
            {formatBytes(stats.storage_savings_bytes)}
          </p>
          <p className="text-sm text-gray-500">
            ({stats.storage_savings_percentage.toFixed(1)}% saved)
          </p>
        </div>
      </div>
    </div>
  );
}; 