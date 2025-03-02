from local_db import sql_db_dal
from models.DTOs.MessageType import MessageType
from models.models import GPowerX
from APIs.RoomManagementAPI import send_private_message_to_every_user_in_Wallet
from models.DTOs.message_dto import MessageDTO

def send_g_power_x_message_to_wallet_room(wallet_id : str):
    """
    Send g_power_x message to every participating user in the wallet.
    """
    wallet = sql_db_dal.get_wallet_by_id(wallet_id)
    g_power_x = wallet.g_power_x # TODO - add g_power_x fetch
    message = MessageDTO(type=MessageType.GPowerX, data=GPowerX(g_power_x=g_power_x))
    return send_private_message_to_every_user_in_Wallet(message=message, wallet_id=wallet_id)

def save_g_power_x_to_db(g_power_x : GPowerX):
    """
    Save g_power_x to db
    """
    return sql_db_dal.insert_g_power_x(g_power_x)
    
