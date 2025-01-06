from fastapi import APIRouter, HTTPException
from db import wallets_collection
import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.get("/wallets/{user_id}")
async def get_user_wallets(user_id: str):
    wallets_cursor = wallets_collection.find({"users.user_id": user_id})
    
    # Convert cursor to a list and serialize ObjectId
    wallets = [
        {
            "wallet_id": wallet["wallet_id"],
            "wallet_name": wallet.get("wallet_name"),
            "threshold" : wallet.get("threshold"),
            "metadata": wallet.get("metadata", {}),
            "users": wallet.get("users", []),
        }
        for wallet in wallets_cursor
    ]
    logger.info(f"Found wallets: {list(wallets)}")
    return [
        {"wallet_id": wallet["wallet_id"], "metadata": wallet["metadata"], "users" : wallet.get("users", [])}
        for wallet in wallets
    ]

@router.post("/wallets/create")
async def create_wallet(wallet_id: str, wallet_name: str, threshold: int, users: list, metadata: dict):
    # Validate the threshold
    if threshold > len(users):
        raise HTTPException(status_code=400, detail="Threshold cannot exceed the number of users")

    # Insert the wallet into the database
    wallet = {
        "wallet_id": wallet_id,
        "wallet_name": wallet_name,
        "threshold": threshold,
        "users": users,
        "metadata": metadata
    }
    wallets_collection.insert_one(wallet)
    return {"message": "Wallet created successfully", "wallet_id": wallet_id}

