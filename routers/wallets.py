from fastapi import APIRouter, HTTPException
import logging
from local_db.sql_db_dal import get_my_wallets, get_friend_by_matrix_id
from APIs.RoomManagementAPI import create_new_wallet #respond_to_room_invitation
from Services.WalletService import get_wallet_users_data
logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/")
async def get_user_wallets():
    # Find wallets containing the user
    
    db_wallets = get_my_wallets()
    wallets = []
    for wallet in db_wallets:
        # Fetch user details for each user in the wallet
        users_data = get_wallet_users_data(wallet)
        wallets.append({
            "wallet_id": wallet.wallet_id,
            "wallet_name": wallet.name,
            "threshold": wallet.threshold,
            "users": users_data
        })
    return wallets

@router.post("/")
async def create_wallet( wallet_name: str, threshold: int, users: list, max_participants: int):
    # Validate the threshold
    
    success, wallet = create_new_wallet(invited_users_emails=users,wallet_name=wallet_name,wallet_threshold=threshold,max_participants=max_participants)
    users_data = get_wallet_users_data(wallet)
    # Insert the wallet into the database
    wallet = {
        "wallet_id": wallet.wallet_id,
        "wallet_name": wallet_name,
        "threshold": threshold,
        "users": users_data,
    }
    
    return {"wallet": wallet}

