import React, { useState, useRef, useEffect } from "react";
import WalletList from "./components/WalletList";
import WalletDetails from "./components/WalletDetails";
import Auth from "./components/Auth";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import { AuthProvider, useAuth } from "./components/AuthContext";
import FriendsList from './components/FriendsList';
import { NotificationProvider, useNotification } from './components/NotificationContext';
import Avatar from "@mui/material/Avatar";

const AppContent = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const { user, logout } = useAuth();
    
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
        <div style={{
            background: 'linear-gradient(160deg, rgba(103, 58, 183, 0.25) 0%, rgba(0, 0, 0, 1) 100%)',
            minHeight: '100vh',
        }}>
            <AppBar 
                position="static" 
                sx={{ 
                    backgroundColor: "rgba(103, 58, 183, 0.25)",
                    boxShadow: 'none',
                    padding: "2px",
                    backdropFilter: "blur(8px)",
                }}
            >
                <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'rgba(103, 58, 183, 0.5)' }}>
                            {user.email[0].toUpperCase()}
                        </Avatar>
                        <Typography 
                            sx={{ 
                                fontSize: "24px", 
                                fontWeight: "bold",
                                color: '#e0e0e0'
                            }}
                        >
                            Welcome, {user.email.split('@')[0]}
                        </Typography>
                    </Box>
                    <Button 
                        color="inherit" 
                        onClick={logout}
                        sx={{ color: '#e0e0e0' }}
                    >
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>
            
            <Box sx={{ 
                display: 'flex',
                height: 'calc(100vh - 68px - 40px)', // Subtract AppBar and footer height
                position: 'relative'
            }}>
                <WalletList userId={user.email} onSelectWallet={setSelectedWallet} />
                {selectedWallet && <WalletDetails wallet={selectedWallet} onClose={() => setSelectedWallet(null)} />}
                <FriendsList />
            </Box>

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
                    height: '40px',
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
