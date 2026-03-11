import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export const propertiesApi = {
  getAll: () => api.get('/properties'),
  getById: (id) => api.get(`/properties/${id}`),
  create: (data) => api.post('/properties', data),
  update: (id, data) => api.put(`/properties/${id}`, data),
  delete: (id) => api.delete(`/properties/${id}`),
};

export const tenantsApi = {
  getAll: () => api.get('/tenants'),
  getById: (id) => api.get(`/tenants/${id}`),
  create: (data) => api.post('/tenants', data),
  update: (id, data) => api.put(`/tenants/${id}`, data),
  delete: (id) => api.delete(`/tenants/${id}`),
};

export const leasesApi = {
  getAll: () => api.get('/leases'),
  create: (data) => api.post('/leases', data),
  update: (id, data) => api.put(`/leases/${id}`, data),
  delete: (id) => api.delete(`/leases/${id}`),
};

export const paymentsApi = {
  getAll: () => api.get('/payments'),
  create: (data) => api.post('/payments', data),
};

export const dashboardApi = {
  getStats: () => api.get('/dashboard'),
};

export default api;
