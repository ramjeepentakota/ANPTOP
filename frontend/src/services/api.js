import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API service functions
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  setupMfa: () => api.post('/auth/mfa/setup'),
  enableMfa: (token) => api.post('/auth/mfa/enable', { token }),
  disableMfa: (token) => api.post('/auth/mfa/disable', { token }),
  changePassword: (oldPassword, newPassword) => 
    api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
};

export const engagementService = {
  list: (params) => api.get('/engagements', { params }),
  get: (id) => api.get(`/engagements/${id}`),
  create: (data) => api.post('/engagements', data),
  update: (id, data) => api.put(`/engagements/${id}`, data),
  delete: (id) => api.delete(`/engagements/${id}`),
  start: (id) => api.post(`/engagements/${id}/start`),
  complete: (id) => api.post(`/engagements/${id}/complete`),
};

export const targetService = {
  list: (engagementId, params) => api.get('/targets', { params: { engagement_id: engagementId, ...params } }),
  get: (id) => api.get(`/targets/${id}`),
  create: (data, engagementId) => api.post('/targets', data, { params: { engagement_id: engagementId } }),
  update: (id, data) => api.put(`/targets/${id}`, data),
  delete: (id) => api.delete(`/targets/${id}`),
};

export const workflowService = {
  list: (params) => api.get('/workflows', { params }),
  get: (id) => api.get(`/workflows/${id}`),
  execute: (data) => api.post('/workflows/execute', data),
  getExecution: (id) => api.get(`/workflows/executions/${id}`),
  listExecutions: (engagementId, params) => 
    api.get('/workflows/executions', { params: { engagement_id: engagementId, ...params } }),
  cancelExecution: (id) => api.post(`/workflows/executions/${id}/cancel`),
  listPending: () => api.get('/workflows/pending'),
};

export const vulnerabilityService = {
  list: (engagementId, params) => api.get('/vulnerabilities', { params: { engagement_id: engagementId, ...params } }),
  get: (id) => api.get(`/vulnerabilities/${id}`),
  create: (data) => api.post('/vulnerabilities', data),
  update: (id, data) => api.put(`/vulnerabilities/${id}`, data),
};

export const evidenceService = {
  list: (engagementId, params) => api.get('/evidence', { params: { engagement_id: engagementId, ...params } }),
  get: (id) => api.get(`/evidence/${id}`),
  upload: (file, data) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(data).forEach(key => formData.append(key, data[key]));
    return api.post('/evidence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  addCustody: (id, action, notes) => 
    api.post(`/evidence/${id}/custody`, { action, notes }),
};

export const reportService = {
  list: (engagementId) => api.get('/reports', { params: { engagement_id: engagementId } }),
  get: (id) => api.get(`/reports/${id}`),
  create: (data) => api.post('/reports', data),
  finalize: (id) => api.post(`/reports/${id}/finalize`),
};

export const approvalService = {
  list: (engagementId) => api.get('/approvals', { params: { engagement_id: engagementId } }),
  listPending: () => api.get('/approvals/pending'),
  process: (id, action, notes) => api.post(`/approvals/${id}/action`, { action, notes }),
};

export const userService = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
};

export const auditService = {
  list: (engagementId, params) => api.get('/audit', { params: { engagement_id: engagementId, ...params } }),
};

// Cloud Security Service
export const cloudService = {
  listFindings: (engagementId, params) => api.get('/cloud/findings', { params: { engagement_id: engagementId, ...params } }),
  getFinding: (id) => api.get(`/cloud/findings/${id}`),
  createFinding: (data) => api.post('/cloud/findings', data),
  updateFinding: (id, data) => api.put(`/cloud/findings/${id}`, data),
  listAssets: (engagementId, params) => api.get('/cloud/assets', { params: { engagement_id: engagementId, ...params } }),
  getSummary: (engagementId) => api.get(`/cloud/summary/${engagementId}`),
};

// Kubernetes Service
export const kubernetesService = {
  listClusters: (engagementId, params) => api.get('/kubernetes/clusters', { params: { engagement_id: engagementId, ...params } }),
  getCluster: (id) => api.get(`/kubernetes/clusters/${id}`),
  createCluster: (data) => api.post('/kubernetes/clusters', data),
  listFindings: (engagementId, params) => api.get('/kubernetes/findings', { params: { engagement_id: engagementId, ...params } }),
  getFinding: (id) => api.get(`/kubernetes/findings/${id}`),
  listPods: (engagementId, params) => api.get('/kubernetes/pods', { params: { engagement_id: engagementId, ...params } }),
  getSummary: (engagementId) => api.get(`/kubernetes/summary/${engagementId}`),
};

// CVE Service
export const cveService = {
  list: (params) => api.get('/cves', { params }),
  get: (id) => api.get(`/cves/${id}`),
  search: (query) => api.get('/cves/search', { params: { q: query } }),
  getByCveId: (cveId) => api.get(`/cves/cve/${cveId}`),
  getKeystones: () => api.get('/cves/keystones'),
};

// API Security Service
export const apiSecurityService = {
  listVulnerabilities: (engagementId, params) => api.get('/api-security/vulnerabilities', { params: { engagement_id: engagementId, ...params } }),
  getVulnerability: (id) => api.get(`/api-security/vulnerabilities/${id}`),
  createVulnerability: (data) => api.post('/api-security/vulnerabilities', data),
  getSummary: (engagementId) => api.get(`/api-security/vulnerabilities/summary/${engagementId}`),
};

// Payment Security Service
export const paymentService = {
  listFindings: (engagementId, params) => api.get('/payment/findings', { params: { engagement_id: engagementId, ...params } }),
  getFinding: (id) => api.get(`/payment/findings/${id}`),
  createFinding: (data) => api.post('/payment/findings', data),
  getPciSummary: (engagementId) => api.get(`/payment/pci-summary/${engagementId}`),
  getTlsCheck: (target) => api.post('/payment/tls-check', { target }),
};

// Social Engineering Service
export const socialEngineeringService = {
  listCampaigns: (engagementId, params) => api.get('/social-engineering/campaigns', { params: { engagement_id: engagementId, ...params } }),
  getCampaign: (id) => api.get(`/social-engineering/campaigns/${id}`),
  createCampaign: (data) => api.post('/social-engineering/campaigns', data),
  updateCampaign: (id, data) => api.put(`/social-engineering/campaigns/${id}`, data),
  getCampaignStats: (id) => api.get(`/social-engineering/campaigns/${id}/stats`),
  submitResult: (data) => api.post('/social-engineering/results', data),
};

export default api;
