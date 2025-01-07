import React, { useState } from "react";
import WalletList from "./components/WalletsList";
import TransactionForm from "./components/TransactionForm";

const App = () => {
    const [selectedWallet, setSelectedWallet] = useState(null);
    const userId = "User1"; // Replace with dynamic user input if needed

    return (
        <div>
            <h1>Bitcoin Threshold Wallet</h1>
            {!selectedWallet ? (
                <WalletList userId={userId} onSelectWallet={setSelectedWallet} />
            ) : (
                <TransactionForm wallet={selectedWallet} userId={userId} />
            )}
            {selectedWallet && (
                <button onClick={() => setSelectedWallet(null)}>
                    Back to Wallet List
                </button>
            )}
        </div>
    );
};

export default App;

