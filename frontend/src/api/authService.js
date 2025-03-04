import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance with default config
export const api = axios.create({
    baseURL: API_URL,
    withCredentials: true // Important for handling cookies
});

// Add request interceptor to add auth token to headers
api.interceptors.request.use(
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

export const authService = {
    async login(email, matrixUserId, password) {
        try {
            const response = await api.post('/login', {
                email,
                matrix_user_id: matrixUserId,
                password
            });
            console.log(response.data);
            if (response.data.access_token) {
                localStorage.setItem('access_token', JSON.stringify(response.data.access_token));
            }
            
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    logout() {
        localStorage.removeItem('access_token');
    },

    getAccessToken() {
        return JSON.parse(localStorage.getItem('access_token'));
    },

    isAuthenticated() {
        const user = this.getAccessToken();
        return !!user && !!user.access_token;
    },

    // Export the configured axios instance for other API calls
    api
}; 