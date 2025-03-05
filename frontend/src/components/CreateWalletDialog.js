import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    OutlinedInput
} from '@mui/material';
import { getFriends } from '../api/api';

const CreateWalletDialog = ({ open, onClose, onSubmit }) => {
    const [formData, setFormData] = useState({
        name: '',
        threshold: 2,
        total_signers: 2,
        selectedFriends: []
    });
    const [error, setError] = useState('');
    const [friends, setFriends] = useState([]);

    useEffect(() => {
        const loadFriends = async () => {
            try {
                const response = await getFriends();
                if (response) {
                    setFriends(response);
                }
            } catch (error) {
                console.error('Error loading friends:', error);
                setError('Failed to load friends list');
            }
        };

        if (open) {
            loadFriends();
        }
    }, [open]);

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

        if (formData.selectedFriends.length === 0) {
            setError('Please select at least one friend');
            return;
        }

        if (formData.selectedFriends.length > formData.total_signers - 1) {
            setError(`You can only select up to ${formData.total_signers - 1} friends`);
            return;
        }

        // Transform the data to match API requirements
        const submitData = {
            wallet_name: formData.name,
            threshold: formData.threshold,
            users: formData.selectedFriends.map(friend => friend.email),
            max_participants: formData.total_signers
        };

        onSubmit(submitData);
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
                        <FormControl fullWidth>
                            <InputLabel id="friends-select-label">Select Friends</InputLabel>
                            <Select
                                labelId="friends-select-label"
                                multiple
                                value={formData.selectedFriends}
                                onChange={(e) => handleChange({
                                    target: {
                                        name: 'selectedFriends',
                                        value: e.target.value
                                    }
                                })}
                                input={<OutlinedInput label="Select Friends" />}
                                renderValue={(selected) => (
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                        {selected.map((friend) => (
                                            <Chip 
                                                key={friend.email} 
                                                label={friend.email} 
                                                sx={{ backgroundColor: 'rgba(103, 58, 183, 0.1)' }}
                                            />
                                        ))}
                                    </Box>
                                )}
                            >
                                {friends.map((friend) => (
                                    <MenuItem key={friend.email} value={friend}>
                                        {friend.email}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
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