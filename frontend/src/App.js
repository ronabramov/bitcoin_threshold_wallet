import React, { useState, useRef, useEffect } from "react";
import WalletList from "./components/WalletList";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import Auth from "./components/Auth";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import { AuthProvider, useAuth } from "./components/AuthContext";
import FriendsList from './components/FriendsList';
import { NotificationProvider, useNotification } from './components/NotificationContext';

const AppContent = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const { user, logout } = useAuth();
    const transactionListRef = useRef();
    const { showNotification } = useNotification();

    useEffect(() => {
        // Make the notification function globally available for the error handler
        window.__showNotification = showNotification;
        return () => {
            delete window.__showNotification;
        };
    }, [showNotification]);

    if (!user) {
        return <Auth />;
    }

    return (
        <div>
            <AppBar 
                position="static" 
                sx={{ 
                    backgroundColor: "rgba(103, 58, 183, 0.25)",
                    boxShadow: 'none',
                    padding: "2px",
                    backdropFilter: "blur(8px)",
                }}
            >
                <Toolbar>
                    <Typography 
                        variant="h6" 
                        component="div" 
                        sx={{ 
                            flexGrow: 1, 
                            color: '#e0e0e0',
                            fontSize: "24px",
                            fontWeight: "bold",
                        }}
                    >
                        Threshold Wallet
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography 
                            sx={{ 
                                fontSize: "24px", 
                                fontWeight: "bold",
                                color: '#e0e0e0'
                            }}
                        >
                            Welcome, {user.email.split('@')[0]}
                        </Typography>
                        <Button 
                            color="inherit" 
                            onClick={logout}
                            sx={{ color: '#e0e0e0' }}
                        >
                            Logout
                        </Button>
                    </Box>
                </Toolbar>
            </AppBar>
            
            <Box sx={{ paddingRight: '300px' }}>
                {!selectedWallet ? (
                    <WalletList userId={user.email} onSelectWallet={setSelectedWallet} />
                ) : (
                    <div style={{ display: "flex" }}>
                        <div style={{ flex: 1, padding: "10px", borderRight: "none" }}>
                            <TransactionList
                                ref={transactionListRef}
                                walletId={selectedWallet.wallet_id}
                                onBackToWallets={() => setSelectedWallet(null)}
                            />
                        </div>

                        <div style={{ flex: 1, padding: "10px" }}>
                            <TransactionForm
                                wallet={selectedWallet}
                                userId={user.email}
                                refreshTransactions={() => {
                                    if (transactionListRef.current) {
                                        transactionListRef.current.fetchTransactions();
                                    }
                                }}
                            />
                        </div>
                    </div>
                )}
            </Box>

            <FriendsList />
            
            <Box
                component="footer"
                sx={{
                    backgroundColor: "rgba(103, 58, 183, 0.25)",
                    color: '#e0e0e0',
                    padding: "2px",
                    textAlign: "center",
                    fontSize: "24px",
                    fontWeight: "bold",
                    position: "fixed",
                    bottom: 0,
                    width: "100%",
                    backdropFilter: "blur(8px)",
                }}
            >
                <Typography variant="body2" sx={{ color: '#e0e0e0' }}>
                    © 2025 Crypto Wallet. All rights reserved.
                </Typography>
            </Box>
        </div>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <NotificationProvider>
                <AppContent />
            </NotificationProvider>
        </AuthProvider>
    );
};

export default App;
