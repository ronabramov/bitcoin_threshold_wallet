import React from 'react';
import {
    Paper,
    Typography,
    Box,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Avatar,
    IconButton,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import CloseIcon from '@mui/icons-material/Close';

const WalletDetails = ({ wallet, onClose }) => {
    if (!wallet) {
        return (
            <Paper
                sx={{
                    backgroundColor: 'rgba(103, 58, 183, 0.25)',
                    backdropFilter: 'blur(8px)',
                    padding: 3,
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                <Typography color="#e0e0e0">Select a wallet to view details</Typography>
            </Paper>
        );
    }

    return (
        <Paper
            sx={{
                backgroundColor: 'rgba(103, 58, 183, 0.25)',
                backdropFilter: 'blur(8px)',
                height: '100%',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column'
            }}
        >
            <Box sx={{ 
                p: 3,
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start'
            }}>
                <Box>
                    <Typography variant="h5" color="#e0e0e0" gutterBottom>
                        {wallet.name || `Wallet ${wallet.wallet_id}`}
                    </Typography>
                    <Typography variant="body1" color="rgba(224, 224, 224, 0.7)">
                        Wallet ID: {wallet.wallet_id}
                    </Typography>
                    <Typography variant="body1" color="rgba(224, 224, 224, 0.7)" sx={{ mt: 1 }}>
                        Threshold: {wallet.threshold}
                    </Typography>
                </Box>
                <IconButton 
                    onClick={onClose}
                    sx={{ 
                        color: '#e0e0e0',
                        '&:hover': {
                            backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        }
                    }}
                >
                    <CloseIcon />
                </IconButton>
            </Box>

            <Box sx={{ p: 3 }}>
                <Typography variant="h6" color="#e0e0e0" gutterBottom>
                    Invited Users
                </Typography>
                <List>
                    {wallet.users.map((user, index) => (
                        <ListItem key={user.matrix_id}>
                            <ListItemAvatar>
                                <Avatar sx={{ bgcolor: 'rgba(103, 58, 183, 0.5)' }}>
                                    {user.email[0].toUpperCase()}
                                </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                                primary={<Typography color="#e0e0e0">{user.email}</Typography>}
                                secondary={<Typography color="rgba(224, 224, 224, 0.7)" variant="body2">{user.matrix_id}</Typography>}
                            />
                        </ListItem>
                    ))}
                </List>
            </Box>
        </Paper>
    );
};

export default WalletDetails; 