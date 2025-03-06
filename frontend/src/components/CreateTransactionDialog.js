import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Typography,
    Box,
} from '@mui/material';
import { createTransaction } from '../api/api';

const CreateTransactionDialog = ({ open, onClose, walletId, onTransactionCreated }) => {
    const [description, setDescription] = useState('');
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (!description.trim()) {
            setError('Description is required');
            setLoading(false);
            return;
        }

        try {
            await createTransaction({
                wallet_id: walletId,
                name: name.trim(),
                description: description.trim()
            });
            onTransactionCreated();
            onClose();
            setDescription('');
        } catch (error) {
            setError('Failed to create transaction');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog 
            open={open} 
            onClose={onClose} 
            maxWidth="sm" 
            fullWidth
        >
            <form onSubmit={handleSubmit}>
                <DialogTitle>Create New Transaction</DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        <TextField
                            label="Name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            fullWidth
                            required
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            label="Description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            fullWidth
                            required
                            multiline
                            rows={4}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '&.Mui-focused fieldset': {
                                        borderColor: 'rgba(103, 58, 183, 0.7)',
                                    },
                                },
                                '& .MuiInputLabel-root': {
                                    '&.Mui-focused': {
                                        color: 'rgba(103, 58, 183, 0.7)',
                                    },
                                },
                            }}
                        />
                        {error && (
                            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                                {error}
                            </Typography>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button 
                        onClick={onClose} 
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={loading}
                        sx={{
                            backgroundColor: 'rgba(103, 58, 183, 0.5)',
                            '&:hover': {
                                backgroundColor: 'rgba(103, 58, 183, 0.7)',
                            },
                        }}
                    >
                        {loading ? 'Creating...' : 'Create Transaction'}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
};

export default CreateTransactionDialog; 