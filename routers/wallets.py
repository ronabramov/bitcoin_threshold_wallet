from fastapi import APIRouter, HTTPException
import logging
from local_db.sql_db_dal import get_my_wallets, get_friend_by_matrix_id
logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.get("/")
async def get_user_wallets(user_id: str):
    # Find wallets containing the user
    
    db_wallets = get_my_wallets()
    wallets = []
    for wallet in db_wallets:
        # Fetch user details for each user in the wallet
        users = wallet.users.split(',')
        users_data = [{"email": get_friend_by_matrix_id(user).email, "matrix_id": user} for user in users]
        wallets.append({
            "wallet_id": wallet.wallet_id,
            "wallet_name": wallet.name,
            "threshold": wallet.threshold,
            "users": users_data
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

