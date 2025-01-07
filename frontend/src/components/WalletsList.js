import React, { useState, useEffect } from "react";
import { getWallets } from "../api/api";

const WalletList = ({ userId, onSelectWallet }) => {
    const [wallets, setWallets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchWallets = async () => {
            try {
                const data = await getWallets(userId);
                setWallets(data);
            } catch (error) {
                console.error("Failed to fetch wallets:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchWallets();
    }, [userId]);

    if (loading) return <p>Loading wallets...</p>;

    return (
        <div>
            <h2>Your Wallets</h2>
            <ul>
                {wallets.map((wallet) => (
                    <li key={wallet.wallet_id}>
                        <button onClick={() => onSelectWallet(wallet)}>
                            {wallet.wallet_name}: {wallet.metadata.description}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default WalletList;
