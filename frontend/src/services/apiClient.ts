import axios from 'axios';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication if needed
apiClient.interceptors.request.use(
  config => {
    // You can add auth token here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Handle common errors here
    if (error.response) {
      // Server responded with an error status code
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened while setting up the request
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
