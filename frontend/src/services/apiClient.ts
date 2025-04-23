import axios from 'axios';

// Create custom error interface to add status property
interface ApiError extends Error {
  status?: number;
}

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for error handling and cache prevention
apiClient.interceptors.request.use(
  config => {
    // Add caching prevention for GET requests
    if (config.method?.toLowerCase() === 'get') {
      config.params = config.params || {};
      config.params['_'] = new Date().getTime();
    }
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
    // Format error messages
    let errorMessage = 'An unknown error occurred';
    if (error.response) {
      // The request was made and the server responded with an error
      const data = error.response.data;
      errorMessage = data.error || data.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = 'No response from server. Please check your connection.';
      console.error('No response from server:', error.request);
    } else {
      // Something else happened while setting up the request
      errorMessage = error.message || errorMessage;
      console.error('Request error:', error);
    }
    
    // Create a custom error with the message
    const customError = new Error(errorMessage) as ApiError;
    customError.name = 'ApiError';
    customError.status = error.response?.status;
    
    return Promise.reject(customError);
  }
);

export default apiClient;