import { apiClient } from "./baseClient";

export const getWallets = async () => {
    const response = await apiClient.get(`/wallets`);
    return response.data;
};

export const createWallet = async ({ wallet_name, threshold, users, max_participants }) => {
    const response = await apiClient.post(`/wallets`, {
        wallet_name,
        threshold,
        users,
        max_participants,
    });
    return response.data;
};

export const createTransaction = async ({ wallet_id, user_id, description }) => {
    const response = await apiClient.post(
        `/transactions`,
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

export const getFriends = async () => {
    const response = await apiClient.get(`/friends`);
    return response.data;
};


export const addFriend = async ({ email, matrix_id }) => {
    const response = await apiClient.post(`/friends`, {
        email,
        matrix_id,
    });
    return response.data;
};

export const removeFriend = async ({ email }) => {
    const response = await apiClient.delete(`/friends`, {
        params: {
            email,
        },
    });
    return response.data;
};
