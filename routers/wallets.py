from fastapi import APIRouter, HTTPException
from db import wallets_collection, users_collection
import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.get("/{user_id}")
async def get_user_wallets(user_id: str):
    # Find wallets containing the user
    wallets_cursor = wallets_collection.find({"users": user_id})
    wallets = []
    for wallet in wallets_cursor:
        # Fetch user details for each user in the wallet
        user_details = list(users_collection.find({ "users": user_id }))
        for user in user_details:
            user["_id"] = str(user["_id"])  # Serialize ObjectId
        wallets.append({
            "wallet_id": wallet["wallet_id"],
            "wallet_name": wallet.get("wallet_name"),
            "threshold": wallet.get("threshold"),
            "metadata": wallet.get("metadata", {}),
            "users": user_details
        })
    return wallets

@router.post("/create")
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

