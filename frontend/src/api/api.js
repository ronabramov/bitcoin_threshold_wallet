import axios from "axios";
import { api } from "./authService";

const API_URL = "https://bitcoin-threshold-wallet.onrender.com"; // render-url
const LOCAL_HOST_URL = "http://127.0.0.1:8000";

export const getWallets = async (userId) => {
    const response = await api.get(`${LOCAL_HOST_URL}/wallets`);
    return response.data;
};

export const createWallet = async ({ wallet_name, threshold, users, max_participants }) => {
    const response = await api.post(`${LOCAL_HOST_URL}/wallets`, {
        wallet_name,
        threshold,
        users,
        max_participants,
    });
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

export const login = async ({ email, matrix_user_id, password }) => {
    const response = await api.post(`${LOCAL_HOST_URL}/login`, {
        email,
        matrix_user_id,
        password,
    });
    return response.data;
};