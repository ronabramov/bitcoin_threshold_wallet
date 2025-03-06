export const withErrorHandler = (apiMethod) => {
    return async (...args) => {
        try {
            return await apiMethod(...args);
        } catch (error) {
            // Get the notification function from the global scope
            // This is a workaround since decorators can't access hooks directly
            const showNotification = window.__showNotification;
            
            if (!showNotification) {
                console.error('Notification system not initialized');
                throw error;
            }

            let errorMessage = 'An unexpected error occurred';

            if (error.response) {
                // Handle server response errors
                const status = error.response.status;
                const detail = error.response.data?.detail;
                debugger
                switch (status) {
                    
                    case 400:
                        errorMessage = detail || 'Invalid request';
                        break;
                    case 401:
                        errorMessage = 'Authentication required';
                        break;
                    case 403:
                        errorMessage = 'You do not have permission to perform this action';
                        break;
                    case 404:
                        errorMessage = 'Resource not found';
                        break;
                    case 409:
                        errorMessage = detail || 'Conflict with existing resource';
                        break;
                    case 500:
                        errorMessage = 'Server error occurred';
                        break;
                    default:
                        errorMessage = detail || `Error: ${status}`;
                }
            } else if (error.request) {
                // Handle network errors
                errorMessage = 'Network error - please check your connection';
            } else {
                errorMessage = error.message;
            }

            showNotification(errorMessage, 'error');
            throw error; // Re-throw the error for the calling code to handle if needed
        }
    };
}; 