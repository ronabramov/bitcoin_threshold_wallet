import axios from "axios";

const API_URL = "https://bitcoin-threshold-wallet.onrender.com"; // render-url
const LOCAL_HOST_URL ="http://127.0.0.1:8000"

export const getWallets = async (userId) => {
    const response = await axios.get(`${LOCAL_HOST_URL}/wallets/${userId}`);
    return response.data;
};

export const createTransaction = async ({ wallet_id, user_id, description }) => {
    const response = await axios.post(
        `${LOCAL_HOST_URL}/transactions/request`,
        null,
        {
            params: {
                wallet_id,
                user_id,
                description,
            },
        }
    );
    return response.data;
};