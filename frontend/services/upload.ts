import apiClient from './api';
import { UploadResponse } from '@/types';
import { useSettingsStore } from '@/store/settingsStore';

export const uploadService = {
  uploadData: async (
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> => {
    const isDemo = useSettingsStore.getState().demoMode;

    if (isDemo) {
      // Simulate network latency & progress updates
      return new Promise<UploadResponse>((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += 20;
          if (onProgress) onProgress(progress);
          
          if (progress >= 100) {
            clearInterval(interval);
            // Simulate random validation errors for realistic testing on specific file names
            if (file.name.includes('invalid') || file.name.includes('error')) {
              resolve({
                success: false,
                message: 'Data validation failed. Standard headers missing.',
                fileId: '',
                fileName: file.name,
                rowCount: 0,
                columnsDetected: [],
                validationErrors: [
                  'Missing required column: "total_revenue"',
                  'Invalid date format on row 42: expected YYYY-MM-DD, got 12/05/2025',
                  'Staff availability count negative on row 105',
                ],
                uploadedAt: new Date().toISOString(),
              });
            } else {
              resolve({
                success: true,
                message: 'Inventory, Order, and Revenue tables successfully validated and synchronized.',
                fileId: `file_${Math.random().toString(36).substr(2, 9)}`,
                fileName: file.name,
                rowCount: 1450,
                columnsDetected: ['date', 'item_id', 'quantity_sold', 'revenue', 'unit_cost', 'staff_on_shift', 'customer_satisfaction'],
                validationErrors: [],
                uploadedAt: new Date().toISOString(),
              });
            }
          }
        }, 300);
      });
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },
};
