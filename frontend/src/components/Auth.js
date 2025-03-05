import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Container, Paper } from '@mui/material';
import { useAuth } from './AuthContext';

const Auth = () => {
    const [formData, setFormData] = useState({
        email: '',
        matrix_user_id: '',
        password: ''
    });
    const [error, setError] = useState('');
    const { login } = useAuth();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        try {
            await login(formData.email, formData.matrix_user_id, formData.password);
        } catch (error) {
            const errorDetail = error.response?.data?.detail;
            if (typeof errorDetail === 'object' && errorDetail.code) {
                switch (errorDetail.code) {
                    case 'INVALID_CREDENTIALS':
                        setError('Incorrect credentials. Please try again.');
                        break;
                    default:
                        setError(errorDetail.message || 'An error occurred during login');
                }
            } else {
                setError(errorDetail || 'An error occurred during login');
            }
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Paper
                    elevation={3}
                    sx={{
                        padding: 4,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    }}
                >
                    <Typography component="h1" variant="h5" color="primary">
                        Sign In
                    </Typography>
                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email Address"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={formData.email}
                            onChange={handleChange}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="matrix_user_id"
                            label="Matrix User ID"
                            name="matrix_user_id"
                            value={formData.matrix_user_id}
                            onChange={handleChange}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            value={formData.password}
                            onChange={handleChange}
                        />
                        {error && (
                            <Typography color="error" sx={{ mt: 1 }}>
                                {error}
                            </Typography>
                        )}
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2 }}
                        >
                            Sign In
                        </Button>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Auth; 