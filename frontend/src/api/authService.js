import { apiClient } from "./baseClient";

export const authService = {
    async login(email, matrixUserId, password) {
        try {
            const response = await apiClient.post('/login', {
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
    }
}; 