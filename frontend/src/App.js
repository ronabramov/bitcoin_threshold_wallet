import React, { useState, useRef } from "react";
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

const AppContent = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const { user, logout } = useAuth();
    const transactionListRef = useRef();

    if (!user) {
        return <Auth />;
    }

    return (
        <div>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} color="#d2e3eb">
                        Threshold Wallet
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography color="#d2e3eb">
                            Welcome, {user.email.split('@')[0]}
                        </Typography>
                        <Button color="inherit" onClick={logout}>
                            Logout
                        </Button>
                    </Box>
                </Toolbar>
            </AppBar>
            
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
            
            <Box
                component="footer"
                sx={{
                    backgroundColor: "rgba(186, 186, 227, 0.46)",
                    color: "#d2e3eb",
                    padding: "2px",
                    textAlign: "center",
                    fontSize: "24px",
                    fontWeight: "bold",
                    position: "fixed",
                    bottom: 0,
                    width: "100%",
                }}
            >
                <Typography variant="body2" color="textSecondary">
                    © 2025 Crypto Wallet. All rights reserved.
                </Typography>
            </Box>
        </div>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
};

export default App;
