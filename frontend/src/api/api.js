import axios from "axios";

const API_URL = "https://bitcoin-threshold-wallet.onrender.com"; // render-url

// Fetch wallets for a user
export const getWallets = async (userId) => {
    const response = await axios.get(`${API_URL}/wallets/wallets/${userId}`);
    return response.data;
};

// Create a new transaction
export const createTransaction = async (data) => {
    const response = await axios.post(`${API_URL}/transactions/transactions/request`, data);
    return response.data;
};
