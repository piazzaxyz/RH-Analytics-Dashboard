import axios, { AxiosError } from 'axios';
import { getToken, removeToken } from './auth';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
});

let isRedirecting = false;

api.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => {
    isRedirecting = false;
    return response;
  },
  (error: AxiosError) => {
    isRedirecting = false;
    if (!error.response) return Promise.reject(error);
    const status = error.response.status;
    const url = error.config?.url || '';
    const hadToken = !!error.config?.headers?.Authorization;
    const rawDetail = error.response?.data?.detail;
    const detail = typeof rawDetail === 'string' ? rawDetail.toLowerCase() : '';

    if (status === 401 && !isRedirecting && hadToken && !url.includes('/auth/login')) {
      const isTokenInvalid = detail.includes('token inválido');
      const isUserInactive = detail.includes('usuário não encontrado ou inativo');
      const isDataRequest = url.includes('/employees') || url.includes('/departments') || url.includes('/positions') || url.includes('/payroll') || url.includes('/dashboard');
      if ((isTokenInvalid || isUserInactive) && !isDataRequest) {
        isRedirecting = true;
        removeToken();
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
