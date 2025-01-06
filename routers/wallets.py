from fastapi import APIRouter
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
