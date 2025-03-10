from Services.Context import Context
from APIs.RoomManagementAPI import send_private_message_to_every_user_in_Wallet
from models.models import delta_i_message as DeltaMessage
from ecdsa import curves
from local_db import sql_db_dal

class StepThreeOperations():
    
    def broadcast_delta_i(delta_i : int, transaction_id, wallet_id):
        delta_i_message = DeltaMessage(delta_i=delta_i, transaction_id= transaction_id)
        send_private_message_to_every_user_in_Wallet(message=delta_i_message, wallet_id=wallet_id)

    def calculate_inversed_delta(delta : int, wallet_id : str):
        curve = curves.curve_by_name(sql_db_dal.get_wallet_by_id(wallet_id=wallet_id).curve_name)
        


