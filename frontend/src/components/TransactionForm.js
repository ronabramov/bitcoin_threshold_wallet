import React, { useState } from "react";
import { createTransaction } from "../api/api";

const TransactionForm = ({ wallet, userId, refreshTransactions }) => {
    const [description, setDescription] = useState("");
    const [status, setStatus] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createTransaction({
                wallet_id: wallet.wallet_id,
                user_id: userId,
                description,
            });
            setStatus("Transaction created successfully.");
            setDescription(""); // Clear the input field
            refreshTransactions(); // Reload the transaction list
        } catch (error) {
            console.error("Failed to create transaction:", error);
            setStatus("Error: Failed to create transaction.");
        }
    };

    return (
        <div>
            <h2>Create Transaction for: {wallet.wallet_name}</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Description:
                    <input
                        type="text"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {status && <p>{status}</p>}
        </div>
    );
};

export default TransactionForm;
