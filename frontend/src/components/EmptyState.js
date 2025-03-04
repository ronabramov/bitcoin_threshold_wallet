import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';

const EmptyState = ({ message, actionLabel, onAction }) => {
    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '60vh',
                padding: 3,
                textAlign: 'center'
            }}
        >
            <Paper
                elevation={0}
                sx={{
                    p: 4,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    borderRadius: 2,
                    maxWidth: 400,
                    width: '100%'
                }}
            >
                <Typography variant="h5" component="h2" gutterBottom>
                    No Wallets Found
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    {message || "You haven't created any wallets yet. Create your first wallet to get started!"}
                </Typography>
                {actionLabel && onAction && (
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={onAction}
                        sx={{ mt: 2 }}
                    >
                        {actionLabel}
                    </Button>
                )}
            </Paper>
        </Box>
    );
};

export default EmptyState; 