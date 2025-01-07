import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000"; // Replace with your backend URL if needed

const TransactionList = forwardRef(({ walletId }, ref) => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTransaction, setSelectedTransaction] = useState(null);

    // Fetch transactions from the backend
    const fetchTransactions = async () => {
        setLoading(true); // Show loading state during fetch
        try {
            const response = await axios.get(`${API_URL}/transactions/${walletId}`);
            const formattedTransactions = response.data.map((tx) => ({
                ...tx,
                id: tx.id || tx._id, // Map backend ID correctly
            }));
            setTransactions(formattedTransactions);
        } catch (error) {
            console.error("Failed to fetch transactions:", error);
        } finally {
            setLoading(false); // Stop loading state
        }
    };

    // Expose the fetchTransactions function to the parent component via ref
    useImperativeHandle(ref, () => ({
        fetchTransactions,
    }));

    useEffect(() => {
        fetchTransactions();
    }, [walletId]);

    // Handle user response (Accept/Decline)
    const handleResponse = async (response) => {
        if (!selectedTransaction || !selectedTransaction.id) {
            console.error("Transaction ID is missing:", selectedTransaction);
            return;
        }

        try {
            const params = {
                transaction_id: selectedTransaction.id, // Use transaction ID from backend
                user_id: "User2", // Replace with dynamic user ID if needed
                acceptence: response === "accept",
            };

            const queryString = new URLSearchParams(params).toString();
            const requestUrl = `${API_URL}/transactions/transactions/respond?${queryString}`;

            await axios.post(requestUrl);
            alert(`Response "${response}" submitted successfully.`);
            setSelectedTransaction(null); // Close the modal
            fetchTransactions(); // Refresh the transaction list
        } catch (error) {
            console.error("Failed to submit response:", error);
            alert("Failed to submit response.");
        }
    };

    if (loading) return <p>Loading transactions...</p>;

    return (
        <div>
            <h2>Transactions for Wallet ID: {walletId}</h2>
            <ul>
                {transactions.map((tx) => (
                    <li key={tx.id}>
                        <strong>Description:</strong> {tx.description} <br />
                        <strong>Status:</strong> {tx.status}
                        {tx.status === "waiting" && (
                            <button
                                style={{ marginLeft: "10px" }}
                                onClick={() => setSelectedTransaction(tx)}
                            >
                                Submit Response
                            </button>
                        )}
                    </li>
                ))}
            </ul>

            {/* Modal for Accept/Decline */}
            {selectedTransaction && (
                <div
                    style={{
                        position: "fixed",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        background: "white",
                        border: "1px solid #ccc",
                        padding: "20px",
                        zIndex: 1000,
                        boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
                    }}
                >
                    <h3>Transaction Details</h3>
                    <p>
                        <strong>Description:</strong> {selectedTransaction.description}
                    </p>
                    <p>
                        <strong>Status:</strong> {selectedTransaction.status}
                    </p>
                    <div style={{ marginTop: "10px" }}>
                        <button
                            style={{ marginRight: "10px", background: "green", color: "white" }}
                            onClick={() => handleResponse("accept")}
                        >
                            Accept
                        </button>
                        <button
                            style={{ background: "red", color: "white" }}
                            onClick={() => handleResponse("decline")}
                        >
                            Decline
                        </button>
                    </div>
                </div>
            )}

            {/* Backdrop for Modal */}
            {selectedTransaction && (
                <div
                    onClick={() => setSelectedTransaction(null)} // Close modal on backdrop click
                    style={{
                        position: "fixed",
                        top: 0,
                        left: 0,
                        width: "100%",
                        height: "100%",
                        background: "rgba(0, 0, 0, 0.5)",
                        zIndex: 999,
                    }}
                />
            )}
        </div>
    );
});

export default TransactionList;
