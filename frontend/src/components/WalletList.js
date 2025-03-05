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
    IconButton
} from '@mui/material';
import { getWallets, createWallet } from '../api/api';
import EmptyState from './EmptyState';
import CreateWalletDialog from './CreateWalletDialog';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

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
            Create your first wallet to get started!
        </Typography>
    </Box>
);

const WalletList = ({ userId, onSelectWallet }) => {
    const [wallets, setWallets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [openDialog, setOpenDialog] = useState(false);

    const fetchWallets = async () => {
        try {
            setLoading(true);
            const response = await getWallets(userId);
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
        } catch (err) {
            // Error will be handled by the error handler decorator
        }
    };

    if (loading) {
        return <Typography>Loading wallets...</Typography>;
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
                <Typography variant="h6" color="#e0e0e0" sx={{ mb: 1 }}>
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
                <List sx={{ flexGrow: 1, overflow: 'auto' }}>
                    {wallets.map((wallet) => (
                        <ListItem key={wallet.wallet_id} disablePadding>
                            <ListItemButton 
                                onClick={() => onSelectWallet(wallet)}
                                sx={{
                                    '&:hover': {
                                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                                    }
                                }}
                            >
                                <ListItemText
                                    primary={wallet.name || `Wallet ${wallet.wallet_id}`}
                                    secondary={`Balance: ${wallet.balance || '0'} BTC`}
                                    primaryTypographyProps={{ color: '#e0e0e0' }}
                                    secondaryTypographyProps={{ color: 'rgba(224, 224, 224, 0.7)' }}
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
