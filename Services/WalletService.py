from local_db import sql_db_dal
from models.DTOs.MessageType import MessageType
from models.models import GPowerX
from APIs.RoomManagementAPI import send_private_message_to_every_user_in_Wallet
from models.DTOs.message_dto import MessageDTO
from Services.Context import Context
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
    users = wallet.users.split(',')
    users_data = [{"email": get_friend_by_matrix_id(user).email, "matrix_id": user} for user in users]
    return users_data