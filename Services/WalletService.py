from local_db import sql_db_dal
from models.DTOs.MessageType import MessageType
from models.models import GPowerX
from APIs.RoomManagementAPI import send_private_message_to_every_user_in_Wallet
from models.DTOs.message_dto import MessageDTO
from Services.Context import Context
from Services.MatrixService import MatrixService
from ecdsa import curves
from local_db.sql_db import Wallet
from local_db.sql_db_dal import get_friend_by_matrix_id

def send_g_power_x_message_to_wallet_room(x : int, wallet : Wallet):
    """
    Send g_power_x message to every participating user in the wallet.
    """
    g = curves.curve_by_name(wallet.curve_name).generator
    X = g * x
    my_matrix_id = Context.matrix_user_id()
    message = MessageDTO(type=MessageType.GPowerX, data=GPowerX(value=X,wallet_id=wallet.wallet_id, user_matrix_id=my_matrix_id))  
    return send_private_message_to_every_user_in_Wallet(message=message, wallet_id=wallet.wallet_id)

def save_incoming_g_power_x_to_db(g_power_x : GPowerX):
    """
    Save g_power_x to db
    """
    return sql_db_dal.insert_g_power_x(g_power_x)
    

def get_wallet_users_data(wallet : Wallet):
    existing_users = MatrixService.instance().get_existing_users_in_room(wallet.wallet_id)
    pending_users = MatrixService.instance().get_invited_users_in_room(wallet.wallet_id)
    users_data = [{"email": get_friend_by_matrix_id(user).email, "matrix_id": user} for user in pending_users], [{"email": get_friend_by_matrix_id(user).email, "matrix_id": user} for user in existing_users if user != Context.matrix_user_id()]
    return users_data

def get_my_wallets():
    db_wallets = sql_db_dal.get_my_wallets()
    wallets = []
    pending_invitations_rooms = MatrixService.instance().get_all_room_invitations()
    
    pending_invitations_rooms = [invitation for invitation in pending_invitations_rooms if invitation["id"] not in [wallet.wallet_id for wallet in db_wallets]]
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