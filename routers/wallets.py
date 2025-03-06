from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from local_db.sql_db_dal import get_my_wallets, get_friend_by_matrix_id
from APIs.RoomManagementAPI import create_new_wallet, respond_to_room_invitation
from Services.WalletService import get_wallet_users_data
from Services.MatrixService import MatrixService


logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/wallets", tags=["wallets"])

class Wallet(BaseModel):
    wallet_name: str
    threshold: int
    users: list[str]
    max_participants: int

class WalletResponse(BaseModel):
    accept: bool

@router.get("/")
def get_user_wallets():
    # Find wallets containing the user
    
    db_wallets = get_my_wallets()
    wallets = []
    pending_invitations_rooms = MatrixService.instance().get_all_room_invitations()
    for wallet in db_wallets:
        # Fetch user details for each user in the wallet
        pending_users_data, existing_users_data  = get_wallet_users_data(wallet)
        wallets.append({
            "wallet_id": wallet.wallet_id,
            "name": wallet.name,
            "threshold": wallet.threshold,
            "existing_users": existing_users_data,
            "pending_users": pending_users_data,
            "status": "active"
        })
    
    for pending_invitation in pending_invitations_rooms:
        wallets.append({
            "wallet_id": pending_invitation["id"],
            "name": MatrixService.remove_prefix_from_room_name(pending_invitation["name"]),
            "threshold": "?",
            "existing_users": [],
            "pending_users": [],
            "status": "pending"
        })
    return wallets

    # set params in the body:
@router.post("/")
async def create_wallet(wallet_payload: Wallet):
    # Validate the threshold
    success, wallet = create_new_wallet(invited_users_emails=wallet_payload.users,wallet_name=wallet_payload.wallet_name,wallet_threshold=wallet_payload.threshold,max_participants=wallet_payload.max_participants)
    # set users to a comma separated string
    
    pending_users_data, existing_users_data = get_wallet_users_data(wallet)
    # Insert the wallet into the database
    if success:
        wallet_response = {
            "wallet_id": wallet.wallet_id,
            "name": wallet.name,
            "threshold": wallet.threshold,
            "existing_users": existing_users_data,
            "pending_users": pending_users_data
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to create wallet")
    
    return wallet_response

# accept is a boolean in the body:
@router.post("/{wallet_id}/respond")
async def respond_to_wallet_invitation(wallet_id: str, response: WalletResponse):
    respond_to_room_invitation(wallet_id, response.accept)
    return 