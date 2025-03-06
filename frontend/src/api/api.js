import { apiClient } from "./baseClient";
import { withErrorHandler } from "./decorators";

export const getWallets = withErrorHandler(async () => {
    const response = await apiClient.get(`/wallets`);
    return response.data;
});

export const createWallet = withErrorHandler(async ({ wallet_name, threshold, users, max_participants }) => {
    const response = await apiClient.post(`/wallets`, {
        wallet_name,
        threshold,
        users,
        max_participants,
    });
    return response.data;
});

export const createTransaction = withErrorHandler(async ({ wallet_id, description, name }) => {
    const response = await apiClient.post(
        `/wallets/${wallet_id}/transactions`,
        {
            description,
            name,
        }
    );
    return response.data;
});

export const getFriends = withErrorHandler(async () => {
    const response = await apiClient.get(`/friends`);
    return response.data;
});

export const addFriend = withErrorHandler(async ({ email, matrix_id }) => {
    const response = await apiClient.post(`/friends`, {
        email,
        matrix_id,
    });
    return response.data;
});

export const removeFriend = withErrorHandler(async ({ email }) => {
    const response = await apiClient.delete(`/friends`, {
        params: {
            email,
        },
    });
    return response.data;
});


export const getTransactions = withErrorHandler(async (wallet_id) => {
    const response = await apiClient.get(`/wallets/${wallet_id}/transactions`);
    return response.data;
});

export const respondToWalletInvitation = withErrorHandler(async (walletId, accept) => {
     await apiClient.post(`/wallets/${walletId}/respond`, {
        accept
    });
    return 
});

