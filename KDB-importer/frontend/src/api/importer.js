import axios from 'axios';

// Debug environment variable
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://kdb-alb-1026840859.us-east-1.elb.amazonaws.com/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const importArxiv = async (inputs, metadata = []) => {
  const response = await api.post('/import', {
    inputs,
    metadata
  });
  return response.data.results;
};


export const searchArxiv = async (payload) => {
  const response = await api.post('/search', payload);
  return response.data.results;
};

export const uploadToPaperless = async (paper, metadata) => {
  const response = await api.post('/paperless/upload', {
    paper,
    metadata
  });
  return response.data.task_id;
};

// Keyword Management API functions
export const extractKeywords = async (paperData) => {
  const response = await api.post('/keywords/extract', {
    paper_data: paperData
  });
  return response.data;
};

export const validateKeywords = async (keywords) => {
  const response = await api.post('/keywords/validate', {
    keywords
  });
  return response.data;
};

export const getAvailableDomains = async () => {
  const response = await api.get('/keywords/domains');
  return response.data;
};

// Dashboard API functions
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const getDashboardAnalytics = async () => {
  const response = await api.get('/dashboard/analytics');
  return response.data;
};

// History API functions
export const getAvailableDates = async () => {
  const response = await api.get('/history/dates');
  return response.data;
};

export const getDocumentHistoryByDate = async (date) => {
  const response = await api.get(`/history/date/${date}`);
  return response.data;
};

export const getDocumentSummaryByRange = async (startDate, endDate) => {
  const response = await api.get(`/history/range?start_date=${startDate}&end_date=${endDate}`);
  return response.data;
};

