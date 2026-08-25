import axios from 'axios';
import { useAuthStore } from '@/stores/auth-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Attach access token to every request
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Refresh token on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { accessToken } = await useAuthStore.getState().refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return apiClient(originalRequest);
      } catch {
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  },
);

// Typed API helpers
export async function get<T>(url: string, params?: Record<string, unknown>) {
  const { data } = await apiClient.get<{ success: boolean; data: T }>(url, { params });
  return data.data;
}

export async function post<T>(url: string, body?: unknown) {
  const { data } = await apiClient.post<{ success: boolean; data: T }>(url, body);
  return data.data;
}

export async function patch<T>(url: string, body?: unknown) {
  const { data } = await apiClient.patch<{ success: boolean; data: T }>(url, body);
  return data.data;
}

export async function del(url: string) {
  await apiClient.delete(url);
}

export async function postForm<T>(url: string, formData: FormData) {
  const { data } = await apiClient.post<{ success: boolean; data: T }>(url, formData, {
    // Let the browser set the multipart boundary; the instance default of
    // 'application/json' would otherwise take precedence and break the upload.
    headers: { 'Content-Type': undefined },
  });
  return data.data;
}
