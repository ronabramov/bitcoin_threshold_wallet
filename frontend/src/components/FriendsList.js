import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    ListItemSecondaryAction,
    Avatar,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    IconButton,
    Paper
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { addFriend, getFriends, removeFriend } from '../api/api';

const EmptyFriendsList = ({ onAddFriend }) => (
    <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '50vh',
            padding: 2,
            textAlign: 'center'
        }}
    >
        <PersonIcon sx={{ fontSize: 60, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
        <Typography variant="h6" color="#e0e0e0" gutterBottom>
            No Friends Added Yet
        </Typography>
        <Typography variant="body2" color="#e0e0e0" sx={{ mb: 2 }}>
            Add friends to collaborate on your wallets
        </Typography>
        
    </Box>
);

const FriendsList = () => {
    const [friends, setFriends] = useState([]); 
    const [openDialog, setOpenDialog] = useState(false);
    const [newFriend, setNewFriend] = useState({
        email: '',
        matrixId: ''
    });
    const [error, setError] = useState('');
    const [isCollapsed, setIsCollapsed] = useState(false);

    useEffect(() => {
        const loadFriends = async () => {
            try {
                const response = await getFriends();
                if (response) {
                    setFriends(response.map(friend => ({
                        email: friend.email,
                        matrixId: friend.matrix_id
                    })));
                }
            } catch (error) {
                console.error('Error loading friends:', error);
                setError('Failed to load friends list');
            }
        };

        loadFriends();
    }, []);

    const handleAddFriend = async () => {
        // Validate inputs
        if (!newFriend.email || !newFriend.matrixId) {
            setError('Please fill in all fields');
            return;
        }
        

        try {
            const response = await addFriend({ 
                email: newFriend.email, 
                matrix_id: newFriend.matrixId 
            });
            
            if (response) {
                setFriends([...friends, {
                    email: newFriend.email,
                    matrixId: newFriend.matrixId,
                }]);
                setNewFriend({ email: '', matrixId: '' });
                setError('');
                setOpenDialog(false);
            }
        } catch (error) {
            setError('Failed to add friend. Please try again.');
            console.error('Error adding friend:', error);
        }
    };

    const handleDeleteFriend = async (email) => {
        try {
            const response = await removeFriend({ email });
            if (response) {
                setFriends(friends.filter(friend => friend.email !== email));
            }
        } catch (error) {
            console.error('Error deleting friend:', error);
            setError('Failed to delete friend');
        }
    };

    return (
        <Paper
            sx={{
                backgroundColor: 'rgba(103, 58, 183, 0.25)',
                backdropFilter: 'blur(8px)',
                width: isCollapsed ? '50px' : '300px',
                position: 'fixed',
                right: 0,
                top: '64px',
                bottom: '20px',
                borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                flexDirection: 'column',
                transition: 'width 0.3s ease-in-out',
                overflow: 'hidden'
            }}
        >
            <Box sx={{ 
                p: 2, 
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
            }}>
                {!isCollapsed && (
                    <>
                        <Typography variant="h6" color="#e0e0e0">
                            Friends
                        </Typography>
                        <Button
                            variant="outlined"
                            startIcon={<PersonAddIcon />}
                            onClick={() => setOpenDialog(true)}
                            sx={{ color: '#e0e0e0', borderColor: '#e0e0e0' }}
                        >
                            Add Friend
                        </Button>
                    </>
                )}
            </Box>

            {!isCollapsed && (
                <>
                    {friends.length === 0 ? (
                        <EmptyFriendsList onAddFriend={() => setOpenDialog(true)} />
                    ) : (
                        <List sx={{ 
                            flexGrow: 1, 
                            overflow: 'auto',
                            '&::-webkit-scrollbar': {
                                width: '8px',
                            },
                            '&::-webkit-scrollbar-track': {
                                background: 'rgba(255, 255, 255, 0.05)',
                            },
                            '&::-webkit-scrollbar-thumb': {
                                background: 'rgba(103, 58, 183, 0.5)',
                                borderRadius: '4px',
                            },
                            '&::-webkit-scrollbar-thumb:hover': {
                                background: 'rgba(103, 58, 183, 0.7)',
                            },
                        }}>
                            {friends.map((friend) => (
                                <ListItem key={friend.email}>
                                    <ListItemAvatar>
                                        <Avatar sx={{ bgcolor: 'rgba(103, 58, 183, 0.5)' }}>
                                            {friend.email[0].toUpperCase()}
                                        </Avatar>
                                    </ListItemAvatar>
                                    <ListItemText
                                        primary={friend.email}
                                        secondary={friend.matrixId}
                                        primaryTypographyProps={{ color: '#e0e0e0' }}
                                        secondaryTypographyProps={{ color: 'rgba(224, 224, 224, 0.7)' }}
                                    />
                                    <ListItemSecondaryAction>
                                        <IconButton
                                            edge="end"
                                            aria-label="delete"
                                            onClick={() => handleDeleteFriend(friend.email)}
                                            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </ListItemSecondaryAction>
                                </ListItem>
                            ))}
                        </List>
                    )}
                </>
            )}

            <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
                <DialogTitle>Add New Friend</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Email Address"
                        type="email"
                        fullWidth
                        value={newFriend.email}
                        onChange={(e) => setNewFriend({ ...newFriend, email: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Matrix ID"
                        fullWidth
                        value={newFriend.matrixId}
                        onChange={(e) => setNewFriend({ ...newFriend, matrixId: e.target.value })}
                    />
                    {error && (
                        <Typography color="error" variant="caption" sx={{ mt: 1 }}>
                            {error}
                        </Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleAddFriend}>Add</Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
};

export default FriendsList; 