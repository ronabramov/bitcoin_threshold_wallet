import React, { useState, useEffect } from 'react';
import { Box, List, ListItem, ListItemText, ListItemButton, Typography, Paper, Button } from '@mui/material';
import { getWallets, createWallet } from '../api/api';
import EmptyState from './EmptyState';
import CreateWalletDialog from './CreateWalletDialog';

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
            setOpenDialog(false); // Only close dialog on success
        } catch (err) {
            // Error will be handled by the error handler decorator
            // Don't close the dialog or update state here
        }
    };

    if (loading) {
        return <Typography>Loading wallets...</Typography>;
    }

    if (wallets.length === 0) {
        return (
            <>
                <EmptyState
                    message="You haven't created any wallets yet. Create your first wallet to get started!"
                    actionLabel="Create New Wallet"
                    onAction={() => setOpenDialog(true)}
                />
                <CreateWalletDialog
                    open={openDialog}
                    onClose={() => setOpenDialog(false)}
                    onSubmit={handleCreateWallet}
                />
            </>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Your Wallets
                </Typography>
                <Button
                    variant="contained"
                    onClick={() => setOpenDialog(true)}
                >
                    Create New Wallet
                </Button>
            </Box>
            <Paper elevation={0} sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
                <List>
                    {wallets.map((wallet) => (
                        <ListItem key={wallet.wallet_id} disablePadding>
                            <ListItemButton onClick={() => onSelectWallet(wallet)}>
                                <ListItemText
                                    primary={wallet.name || `Wallet ${wallet.wallet_id}`}
                                    secondary={`Balance: ${wallet.balance || '0'} BTC`}
                                />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            </Paper>
            <CreateWalletDialog
                open={openDialog}
                onClose={() => setOpenDialog(false)}
                onSubmit={handleCreateWallet}
            />
        </Box>
    );
};

export default WalletList;
