import axios from 'axios';

const API_URL = `http://localhost:${process.env.REACT_APP_PORT}`;
console.log(API_URL);

// Create axios instance with default config
export const apiClient = axios.create({
    baseURL: API_URL,
    withCredentials: true // Important for handling cookies
});

// Add request interceptor to add auth token to headers
apiClient.interceptors.request.use(
    (config) => {
        const accessToken = JSON.parse(localStorage.getItem('access_token'));
        if (accessToken) {
            config.headers.setAuthorization(`Bearer ${accessToken}`);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle 401 responses
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Don't redirect if we're already handling login errors
            const isLoginRequest = error.config.url.includes('/login');
            if (!isLoginRequest) {
                // Clear the access token
                localStorage.removeItem('access_token');
                // Redirect to login page
                window.location.href = '/';
            }
        }
        return Promise.reject(error);
    }
);

