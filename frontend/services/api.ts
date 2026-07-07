import axios from 'axios';
import { useSettingsStore } from '@/store/settingsStore';
import { useAuthStore } from '@/store/authStore';

const apiClient = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Dynamic Base URL & Auth Token mapping
apiClient.interceptors.request.use(
  (config) => {
    // Dynamically retrieve base URL from settings state
    const { apiBaseUrl } = useSettingsStore.getState();
    config.baseURL = apiBaseUrl;

    // Attach Authorization header if token exists
    const { token } = useAuthStore.getState();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Centralized error logic
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If unauthorized, can trigger logout
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    
    const customError = {
      message: error.response?.data?.detail || error.response?.data?.message || 'An error occurred during communication with Chronos services.',
      status: error.response?.status || 500,
      originalError: error,
    };
    return Promise.reject(customError);
  }
);

export default apiClient;
