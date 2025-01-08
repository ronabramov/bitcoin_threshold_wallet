import React, { useState, useRef } from "react";
import WalletList from "./components/WalletList";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

``
const App = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const transactionListRef = useRef(); // Reference to the TransactionList component
    const userId = "User1"; // Replace with dynamic user input if needed

    // Trigger the transaction list to refresh
    const refreshTransactions = () => {
        if (transactionListRef.current) {
            transactionListRef.current.fetchTransactions();
        }
    };

    return (
        <div>
            <AppBar position="static">
                <Toolbar >
                    <Typography variant="h6" component="div" color="#d2e3eb">
                        Threshold Wallet
                    </Typography>
                </Toolbar>
            </AppBar>
            <h1>ECDSA Threshold Wallet</h1>
            {!selectedWallet ? (
                <WalletList userId={userId} onSelectWallet={setSelectedWallet} />
            ) : (
                <div style={{ display: "flex" }}>
                    {/* Left side: Transactions */}
                    <div style={{ flex: 1, padding: "10px", borderRight: "none" }}>
                        <TransactionList
                            ref={transactionListRef}
                            walletId={selectedWallet.wallet_id}
                            onBackToWallets={() => setSelectedWallet(null)} // Pass function to go back
                        />
                    </div>

                    {/* Right side: New Transaction Form */}
                    <div style={{ flex: 1, padding: "10px" }}>
                        <TransactionForm
                            wallet={selectedWallet}
                            userId={userId}
                            refreshTransactions={refreshTransactions}
                        />
                    </div>
                    <Box
                        component="footer"
                        sx={{
                            backgroundColor: "rgba(186, 186, 227, 0.46)", // Translucent navy blue
                            color: "#d2e3eb", // Light blue for text
                            padding: "2px",
                            textAlign: "center",
                            fontSize: "24px",
                            fontWeight: "bold",
                        }}
                    >
                        <Typography variant="body2" color="textSecondary">
                            © 2025 Crypto Wallet. All rights reserved.
                        </Typography>
                    </Box>
                </div>
            )}

        </div>
    );
};

export default App;
