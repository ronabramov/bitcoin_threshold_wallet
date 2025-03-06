import React, { useState, useEffect } from 'react';
import {
    Box,
    List,
    ListItem,
    ListItemText,
    ListItemButton,
    Typography,
    Paper,
    Button,
    IconButton,
    Chip,
    Stack,
    Tooltip,
    CircularProgress
} from '@mui/material';
import { getWallets, createWallet, respondToWalletInvitation } from '../api/api';
import CreateWalletDialog from './CreateWalletDialog';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { useNotification } from './NotificationContext';

const EmptyWalletList = ({ onCreateWallet }) => (
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
        <AccountBalanceWalletIcon sx={{ fontSize: 60, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
        <Typography variant="h6" color="#e0e0e0" gutterBottom>
            No Wallets Created Yet
        </Typography>
        <Typography variant="body2" color="#e0e0e0" sx={{ mb: 2 }}>
            Create your first wallet to get started
        </Typography>
    </Box>
);

const WalletList = ({ userId, onSelectWallet }) => {
    const [wallets, setWallets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [openDialog, setOpenDialog] = useState(false);
    const { showNotification } = useNotification();

    const fetchWallets = async () => {
        try {
            setLoading(true);
            const response = await getWallets();
            setWallets(response);
        } catch (err) {
            // Error will be handled by the error handler decorator
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchWallets();
    }, [userId]);

    const handleCreateWallet = async (walletData) => {
        try {
            const newWallet = await createWallet(walletData);
            setWallets([...wallets, newWallet]);
            setOpenDialog(false);
            showNotification('Wallet created successfully!', 'success');
        } catch (err) {
            // Error will be handled by the error handler decorator
        }
    };

    const handleWalletResponse = async (walletId, accept) => {
        try {
            await respondToWalletInvitation(walletId, accept);
            showNotification(`Wallet invitation ${accept ? 'accepted' : 'rejected'} successfully!`, 'success');
            fetchWallets(); // Refresh the wallet list
        } catch (err) {
            // Error will be handled by the error handler decorator
        }
    };

    if (loading) {
        return (
            <Paper
                sx={{
                    backgroundColor: 'rgba(103, 58, 183, 0.25)',
                    backdropFilter: 'blur(8px)',
                    width: '300px',
                    position: 'fixed',
                    left: 0,
                    top: '64px',
                    bottom: '20px',
                    borderRight: '1px solid rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    gap: 2
                }}>
                    <CircularProgress 
                        sx={{ 
                            color: 'rgba(224, 224, 224, 0.7)',
                            mb: 2
                        }} 
                    />
                    <Typography 
                        color="rgba(224, 224, 224, 0.7)"
                        variant="body1"
                    >
                        Loading wallets...
                    </Typography>
                </Box>
            </Paper>
        );
    }

    return (
        <Paper
            sx={{
                backgroundColor: 'rgba(103, 58, 183, 0.25)',
                backdropFilter: 'blur(8px)',
                width: '300px',
                position: 'fixed',
                left: 0,
                top: '64px',
                bottom: '20px',
                borderRight: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                flexDirection: 'column',
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
                <Typography variant="h6" color="#e0e0e0">
                    Wallets
                </Typography>
                <Button
                    variant="outlined"
                    startIcon={<AccountBalanceWalletIcon />}
                    onClick={() => setOpenDialog(true)}
                    sx={{ color: '#e0e0e0', borderColor: '#e0e0e0' }}
                >
                    New Wallet
                </Button>
            </Box>

            {wallets.length === 0 ? (
                <EmptyWalletList onCreateWallet={() => setOpenDialog(true)} />
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
                    {wallets.map((wallet) => (
                        <ListItem key={wallet.wallet_id} disablePadding>
                            <ListItemButton 
                                key={`button-${wallet.wallet_id}`}
                                onClick={() => wallet.status !== 'pending' && onSelectWallet(wallet)}
                                sx={{
                                    '&:hover': {
                                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                                    }
                                }}
                            >
                                <ListItemText
                                    primary={
                                        <Typography
                                            component="span"
                                            sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                                            color="#e0e0e0"
                                        >
                                            {wallet.name || `Wallet ${wallet.wallet_id}`}
                                            {wallet.status === 'pending' && (
                                                <Chip 
                                                    label="Pending" 
                                                    size="small" 
                                                    color="warning"
                                                    sx={{ 
                                                        backgroundColor: 'rgba(255, 152, 0, 0.2)',
                                                        color: '#ffa726',
                                                        '& .MuiChip-label': {
                                                            px: 1
                                                        }
                                                    }}
                                                />
                                            )}
                                        </Typography>
                                    }
                                    secondary={
                                        wallet.status === 'pending' ? (
                                            <Typography
                                                component="span"
                                                color="rgba(224, 224, 224, 0.7)"
                                            >
                                                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                                                    <Tooltip title="Accept wallet invitation">
                                                        <IconButton
                                                            size="small"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleWalletResponse(wallet.wallet_id, true);
                                                            }}
                                                            sx={{ 
                                                                color: 'rgba(224, 224, 224, 0.7)',
                                                                '&:hover': {
                                                                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                                                    color: '#e0e0e0'
                                                                }
                                                            }}
                                                        >
                                                            <CheckCircleIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Reject wallet invitation">
                                                        <IconButton
                                                            size="small"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleWalletResponse(wallet.wallet_id, false);
                                                            }}
                                                            sx={{ 
                                                                color: 'rgba(224, 224, 224, 0.7)',
                                                                '&:hover': {
                                                                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                                                    color: '#e0e0e0'
                                                                }
                                                            }}
                                                        >
                                                            <CancelIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                </Stack>
                                            </Typography>
                                        ) : (
                                            <Typography color="#e0e0e0">
                                                Threshold: {wallet.threshold}
                                            </Typography>
                                        )
                                    }
                                />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            )}

            <CreateWalletDialog
                open={openDialog}
                onClose={() => setOpenDialog(false)}
                onSubmit={handleCreateWallet}
            />
        </Paper>
    );
};

export default WalletList;
