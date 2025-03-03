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

const App = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const [user, setUser] = useState(null);
    const transactionListRef = useRef();

    const handleLogout = () => {
        setUser(null);
        setSelectedWallet(null);
    };

    const handleAuthSuccess = (userData) => {
        setUser(userData);
    };

    if (!user) {
        return <Auth onAuthSuccess={handleAuthSuccess} />;
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
                            Welcome, {user.user_name || user.email}
                        </Typography>
                        <Button color="inherit" onClick={handleLogout}>
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

export default App;
