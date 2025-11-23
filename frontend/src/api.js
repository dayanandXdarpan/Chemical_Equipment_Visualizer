import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (userData) => api.post('/auth/register/', userData),
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  changePassword: (data) => api.post('/auth/change-password/', data),
  updateProfile: (data) => api.put('/auth/update-profile/', data),
  deleteAccount: () => api.delete('/auth/delete-account/'),
  passwordResetRequest: (data) => api.post('/auth/password-reset/request/', data),
  passwordResetVerify: (data) => api.post('/auth/password-reset/verify/', data),
  passwordResetReset: (data) => api.post('/auth/password-reset/reset/', data),
};

export const datasetAPI = {
  uploadCSV: (formData) => {
    return axios.post(`${API_BASE_URL}/datasets/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getDatasets: () => api.get('/datasets/'),
  getDataset: (id) => api.get(`/datasets/${id}/`),
  getSummary: (id) => api.get(`/datasets/${id}/summary/`),
  getAdvancedStats: (id) => api.get(`/datasets/${id}/advanced_stats/`),
  exportData: (id, format) => api.get(`/datasets/${id}/export/?format=${format}`, { responseType: 'blob' }),
  filterEquipment: (id, params) => api.get(`/datasets/${id}/filter_equipment/?${params}`),
  deleteDataset: (id) => api.delete(`/datasets/${id}/`),
};

export default api;
