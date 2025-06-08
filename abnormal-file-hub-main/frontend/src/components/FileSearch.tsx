import React, { useState, useEffect } from 'react';
import { SearchFilters } from '../services/fileService';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface FileSearchProps {
  onSearch: (filters: SearchFilters) => void;
}

export const FileSearch: React.FC<FileSearchProps> = ({ onSearch }) => {
  const [filters, setFilters] = useState<SearchFilters>({});
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear previous timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    // Set new timeout for real-time search
    if (name === 'filename') {
      const timeout = setTimeout(() => {
        onSearch({ ...filters, [name]: value });
      }, 300); // 300ms delay
      setSearchTimeout(timeout);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  const handleReset = () => {
    setFilters({});
    onSearch({});
  };

  const clearFilename = () => {
    setFilters(prev => ({ ...prev, filename: '' }));
    onSearch({ ...filters, filename: '' });
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTimeout]);

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700">Filename</label>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                name="filename"
                value={filters.filename || ''}
                onChange={handleInputChange}
                className="block w-full pl-10 pr-10 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Search by filename..."
              />
              {filters.filename && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={clearFilename}
                    className="text-gray-400 hover:text-gray-500"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">File Type</label>
            <input
              type="text"
              name="fileType"
              value={filters.fileType || ''}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="e.g., image/jpeg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date Range</label>
            <select
              name="dateRange"
              value={filters.dateRange || ''}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="">All time</option>
              <option value="today">Today</option>
              <option value="week">Last 7 days</option>
              <option value="month">Last 30 days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Min Size (bytes)</label>
            <input
              type="number"
              name="minSize"
              value={filters.minSize || ''}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Minimum size"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Max Size (bytes)</label>
            <input
              type="number"
              name="maxSize"
              value={filters.maxSize || ''}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Maximum size"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={handleReset}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Reset
          </button>
          <button
            type="submit"
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Search
          </button>
        </div>
      </form>
    </div>
  );
}; 