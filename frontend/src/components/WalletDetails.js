import React, { useState } from 'react';
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
    Button,
    Tooltip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import { getTransactions } from '../api/api';
import CreateTransactionDialog from './CreateTransactionDialog';

const TransactionsPanel = ({ wallet, isOpen }) => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [openCreateDialog, setOpenCreateDialog] = useState(false);

    const fetchTransactions = async () => {
        try {
            const data = await getTransactions(wallet.wallet_id);
            setTransactions(data);
        } catch (error) {
            console.error('Failed to fetch transactions:', error);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        if (isOpen) {
            fetchTransactions();
        }
    }, [isOpen, wallet.wallet_id]);

    if (!isOpen) return null;

    return (
        <>
            <Paper
                sx={{
                    backgroundColor: 'rgba(103, 58, 183, 0.25)',
                    backdropFilter: 'blur(8px)',
                    width: '340px',
                    position: 'fixed',
                    left: '700px',
                    top: '64px',
                    bottom: '20px',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    borderRight: '1px solid rgba(255, 255, 255, 0.1)'
                }}
            >
                <Box sx={{ 
                    p: 2,
                    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <Typography variant="h6" color="#e0e0e0">
                        Transactions
                    </Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => setOpenCreateDialog(true)}
                        sx={{ 
                            backgroundColor: 'rgba(103, 58, 183, 0.5)',
                            '&:hover': {
                                backgroundColor: 'rgba(103, 58, 183, 0.7)'
                            }
                        }}
                    >
                        New Transaction
                    </Button>
                </Box>

                <Box sx={{ 
                    p: 3,
                    flexGrow: 1,
                    overflowY: 'auto',
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
                }}>
                    {loading ? (
                        <Typography color="rgba(224, 224, 224, 0.7)">Loading transactions...</Typography>
                    ) : transactions.length === 0 ? (
                        <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '50vh',
                            textAlign: 'center'
                        }}>
                            <AccountBalanceIcon sx={{ fontSize: 60, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
                            <Typography color="#e0e0e0" variant="h6" gutterBottom>
                                No Transactions Yet
                            </Typography>
                            <Typography color="rgba(224, 224, 224, 0.7)" variant="body2">
                                Create your first transaction to get started
                            </Typography>
                        </Box>
                    ) : (
                        <List>
                            {transactions.map((transaction) => (
                                <ListItem
                                    key={transaction.id}
                                    sx={{
                                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                        borderRadius: '8px',
                                        mb: 1,
                                    }}
                                >
                                    <ListItemText
                                        primary={
                                            <Typography color="#e0e0e0">
                                                {transaction.description}
                                            </Typography>
                                        }
                                        secondary={
                                            <Typography color="rgba(224, 224, 224, 0.7)" variant="body2">
                                                Status: {transaction.status}
                                            </Typography>
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    )}
                </Box>
            </Paper>
            <CreateTransactionDialog
                open={openCreateDialog}
                onClose={() => setOpenCreateDialog(false)}
                walletId={wallet.wallet_id}
                onTransactionCreated={fetchTransactions}
            />
        </>
    );
};

const WalletDetails = ({ wallet, onClose }) => {
    const [showTransactions, setShowTransactions] = useState(false);
    const hasPendingUsers = wallet?.pending_users?.length > 0;

    if (!wallet) {
        return (
            <Paper
                sx={{
                    backgroundColor: 'rgba(103, 58, 183, 0.25)',
                    backdropFilter: 'blur(8px)',
                    width: '300px',
                    position: 'fixed',
                    left: '300px',
                    top: '64px',
                    bottom: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRight: '1px solid rgba(255, 255, 255, 0.1)'
                }}
            >
                <Typography color="#e0e0e0">Select a wallet to view details</Typography>
            </Paper>
        );
    }

    return (
        <>
            <Paper
                sx={{
                    backgroundColor: 'rgba(103, 58, 183, 0.25)',
                    backdropFilter: 'blur(8px)',
                    width: '400px',
                    position: 'fixed',
                    left: '300px',
                    top: '64px',
                    bottom: '20px',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    borderRight: '1px solid rgba(255, 255, 255, 0.1)'
                }}
            >
                <Box sx={{ 
                    p: 2,
                    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    height: '70px'
                }}>
                        <Typography variant="h6" color="#e0e0e0" >
                            {wallet.name || `Wallet ${wallet.wallet_id}`}
                        </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title={hasPendingUsers ? 
                            "Transactions are disabled while there are pending users in the wallet" : 
                            "View wallet transactions"
                        }>
                            <span> {/* Wrapper needed for disabled Tooltip */}
                                <IconButton
                                    onClick={() => setShowTransactions(!showTransactions)}
                                    disabled={hasPendingUsers}
                                    sx={{ 
                                        color: showTransactions ? 'primary.main' : '#e0e0e0',
                                        '&:hover': {
                                            backgroundColor: 'rgba(255, 255, 255, 0.1)'
                                        },
                                        '&.Mui-disabled': {
                                            color: 'rgba(224, 224, 224, 0.3)'
                                        }
                                    }}
                                >
                                    <AccountBalanceIcon />
                                </IconButton>
                            </span>
                        </Tooltip>
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
                </Box>
                <Box sx={{ p: 3, 
                    borderBottom: '1px solid rgba(255, 255, 255, 0.1)' ,
                    }}>
                <Typography variant="body1" color="rgba(224, 224, 224, 0.7)">
                            Wallet ID: {wallet.wallet_id}
                        </Typography>
                        <Typography variant="body1" color="rgba(224, 224, 224, 0.7)" sx={{ mt: 1 }}>
                            Threshold: {wallet.threshold}
                        </Typography>
                </Box>
                <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="#e0e0e0" gutterBottom>
                        Existing Users
                    </Typography>
                    <Box sx={{ 
                        maxHeight: 'calc(100vh - 300px)',
                        overflowY: 'auto',
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
                    }}>
                        {wallet.existing_users.length === 0 ? (
                            <Box sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                py: 4,
                                textAlign: 'center'
                            }}>
                                <Typography color="#e0e0e0" variant="body1" gutterBottom>
                                    No Existing Users
                                </Typography>
                                <Typography color="rgba(224, 224, 224, 0.7)" variant="body2">
                                    Users who have joined the wallet will appear here
                                </Typography>
                            </Box>
                        ) : (
                            <List>
                                {wallet.existing_users.map((user, index) => (
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
                        )}
                    </Box>
                </Box>
                <Box sx={{ p: 3 }}>
                    <Typography variant="h6" color="#e0e0e0" gutterBottom>
                            Pending Users
                    </Typography>
                    <Box sx={{ 
                        maxHeight: 'calc(100vh - 300px)',
                        overflowY: 'auto',
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
                    }}>
                        {wallet.pending_users.length === 0 ? (
                            <Box sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                py: 4,
                                textAlign: 'center'
                            }}>
                                <Typography color="#e0e0e0" variant="body1" gutterBottom>
                                    No Pending Users
                                </Typography>
                                <Typography color="rgba(224, 224, 224, 0.7)" variant="body2">
                                    Invited users who haven't joined yet will appear here
                                </Typography>
                            </Box>
                        ) : (
                            <List>
                                {wallet.pending_users.map((user, index) => (
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
                        )}
                    </Box>
                </Box>
            </Paper>
            <TransactionsPanel wallet={wallet} isOpen={showTransactions} />
        </>
    );
};

export default WalletDetails; 