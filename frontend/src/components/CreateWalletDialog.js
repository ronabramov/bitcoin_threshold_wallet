import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    Typography
} from '@mui/material';

const CreateWalletDialog = ({ open, onClose, onSubmit }) => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        threshold: 2,
        total_signers: 3
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        // Validate inputs
        if (!formData.name.trim()) {
            setError('Wallet name is required');
            return;
        }

        if (formData.threshold > formData.total_signers) {
            setError('Threshold cannot be greater than total signers');
            return;
        }

        onSubmit(formData);
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Create New Wallet</DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <TextField
                            label="Wallet Name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            fullWidth
                            required
                        />
                        <TextField
                            label="Description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            fullWidth
                            multiline
                            rows={2}
                        />
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField
                                label="Threshold"
                                name="threshold"
                                type="number"
                                value={formData.threshold}
                                onChange={handleChange}
                                fullWidth
                                required
                                inputProps={{ min: 1 }}
                            />
                            <TextField
                                label="Total Signers"
                                name="total_signers"
                                type="number"
                                value={formData.total_signers}
                                onChange={handleChange}
                                fullWidth
                                required
                                inputProps={{ min: 1 }}
                            />
                        </Box>
                        {error && (
                            <Typography color="error" variant="body2">
                                {error}
                            </Typography>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <Button type="submit" variant="contained" color="primary">
                        Create Wallet
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
};

export default CreateWalletDialog; 