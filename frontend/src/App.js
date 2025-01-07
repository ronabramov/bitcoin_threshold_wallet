import React, { useState, useRef } from "react";
import WalletList from "./components/WalletList";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";

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
            <h1>Bitcoin Threshold Wallet</h1>
            {!selectedWallet ? (
                <WalletList userId={userId} onSelectWallet={setSelectedWallet} />
            ) : (
                <div style={{ display: "flex" }}>
                    {/* Left side: Transactions */}
                    <div style={{ flex: 1, padding: "10px", borderRight: "1px solid #ccc" }}>
                        <TransactionList
                            ref={transactionListRef}
                            walletId={selectedWallet.wallet_id}
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
                </div>
            )}
            {selectedWallet && (
                <button onClick={() => setSelectedWallet(null)}>Back to Wallet List</button>
            )}
        </div>
    );
};

export default App;
