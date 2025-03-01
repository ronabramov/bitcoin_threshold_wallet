import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";

const API_URL = "http://127.0.0.1:8000"; // Replace with your backend URL if needed

const TransactionList = forwardRef(({ walletId, onBackToWallets }, ref) => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTransaction, setSelectedTransaction] = useState(null);

    // Fetch transactions from the backend
    const fetchTransactions = async () => {
        setLoading(true);
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
            setLoading(false);
        }
    };

    // Expose the fetchTransactions function
    useImperativeHandle(ref, () => ({
        fetchTransactions,
    }));

    useEffect(() => {
        fetchTransactions();
    }, [walletId]);

    const handleResponse = async (response) => {
        if (!selectedTransaction || !selectedTransaction.id) {
            console.error("Transaction ID is missing:", selectedTransaction);
            return;
        }

        try {
            const params = {
                transaction_id: selectedTransaction.id,
                user_id: "User2", // Replace with dynamic user ID if needed
                acceptence: response === "accept",
            };

            const queryString = new URLSearchParams(params).toString();
            const requestUrl = `${API_URL}/transactions/transactions/respond?${queryString}`;

            await axios.post(requestUrl);
            alert(`Response "${response}" submitted successfully.`);
            setSelectedTransaction(null); // Close the dialog
            fetchTransactions(); // Refresh the transaction list
        } catch (error) {
            console.error("Failed to submit response:", error);
            alert("Failed to submit response.");
        }
    };

    if (loading) return <p>Loading transactions...</p>;

    return (
        <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
            {/* Scrollable Transactions Section */}
            <Box
                 sx={{
                    flex: 1,
                    overflowY: "scroll", // Enable scrolling
                    padding: "10px",
                    backgroundColor: "rgba(249, 249, 249, 0.02)",
                    "::-webkit-scrollbar": {
                        display: "none", // Hide scrollbar for Webkit-based browsers
                    },
                    scrollbarWidth: "none", // Hide scrollbar for Firefox
                }}
            >
                <h2>Transactions for Wallet ID: {walletId}</h2>
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "15px", // Space between transactions
                    }}
                >
                    {transactions.map((tx, index) => (
                        <Box
                            key={tx.id}
                            sx={{
                                backgroundColor: index % 2 === 0 ? "rgba(82, 107, 183, 0.32)" : "rgba(152, 184, 207, 0.33)", // Alternating colors
                                padding: "15px",
                                borderRadius: "10px",
                                boxShadow: "0 2px 5px rgba(0, 0, 0, 0.01)",
                            }}
                        >
                            <strong>Description:</strong> {tx.description} <br />
                            <strong>Status:</strong> {tx.status}
                            {tx.status === "waiting" && (
                                <Button
                                    variant="contained"
                                    color="primary"
                                    sx={{ marginTop: "5px" }}
                                    onClick={() => setSelectedTransaction(tx)}
                                >
                                    Submit Response
                                </Button>
                            )}
                        </Box>
                    ))}
                </Box>
            </Box>

            {/* Fixed Back to Wallets Button */}
            <Box
                sx={{
                    position: "fixed",
                    bottom: 0,
                    left: 0,
                    right: 0,
                    backgroundColor: "rgba(245, 245, 245, 0)",
                    borderTop: "none",
                    padding: "10px",
                    textAlign: "center",
                }}
            >
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={onBackToWallets} // Call the provided back-to-wallets handler
                >
                    Back to Wallets List
                </Button>
            </Box>

            {/* Material UI Dialog for Accept/Decline */}
            {selectedTransaction && (
                <Dialog
                    open={Boolean(selectedTransaction)}
                    onClose={() => setSelectedTransaction(null)} // Close dialog on backdrop click
                >
                    <DialogTitle>Transaction Details</DialogTitle>
                    <DialogContent>
                        <p>
                            <strong>Description:</strong> {selectedTransaction.description}
                        </p>
                        <p>
                            <strong>Status:</strong> {selectedTransaction.status}
                        </p>
                    </DialogContent>
                    <DialogActions>
                        <Button
                            variant="contained"
                            color="success"
                            onClick={() => handleResponse("accept")}
                        >
                            Accept
                        </Button>
                        <Button
                            variant="contained"
                            color="error"
                            onClick={() => handleResponse("decline")}
                        >
                            Decline
                        </Button>
                    </DialogActions>
                </Dialog>
            )}
        </Box>
    );
});

export default TransactionList;
