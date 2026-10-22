import axios, { type AxiosInstance, type AxiosError } from 'axios';

const getApiBaseUrl = (): string => {
  const url = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (url && url.trim()) {
    let cleaned = url.trim().replace(/\/$/, '');
    if (cleaned.endsWith('/api/v1')) {
      cleaned = cleaned.substring(0, cleaned.length - 7);
    }
    return cleaned;
  }
  // In production browser environments, require explicit VITE_API_BASE_URL configuration
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    console.error(
      'AgentTrust OS Configuration Error: VITE_API_BASE_URL environment variable is not defined for production build.'
    );
    return window.location.origin;
  }
  return 'http://127.0.0.1:8000';
};

const API_BASE_URL = getApiBaseUrl();

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL.replace(/\/$/, '')}/api/v1`,
  timeout: Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS) || 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach bearer token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for automatic 401 token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Do NOT trigger refresh logic if the request itself was an authentication endpoint
    const requestUrl = originalRequest?.url || '';
    if (requestUrl.includes('/auth/login') || requestUrl.includes('/auth/refresh')) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('agenttrust_auth_user');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
