from local_db import sql_db_dal
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.message_dto import MessageDTO
from models.DTOs.MessageType import MessageType
from models.transaction_status import TransactionStatus
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from Services.TransactionService import handle_reached_threshold_transaction
import uuid
from Services.MatrixService import MatrixService
from Services import TransactionService
from Services.Context import Context
from fastapi import HTTPException

"""
This is the APIs the controller should reach for any transaction service
Methods:
1. generate_transaction_and_send_to_wallet
2. respond_to_new_transaction
"""
def generate_transaction_and_send_to_wallet( wallet_id, transaction_details, name, amount: int = None) -> bool:
    """
    * Generate new transaction
    * Saves transaction in local_db 
    * Send to corresponding wallet.

    Return True iff all stages done successfully.  
    """
    user_id = Context.matrix_user_id()
    # check if all users approve the wallet
    invited_users = MatrixService.instance().get_invited_users_in_room(wallet_id)
    if len(invited_users) > 0:
        raise HTTPException(status_code=400, detail="cannot generate transaction, there are invited users in the wallet")
    
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details,amount=amount, wallet_id=wallet_id, shrunken_secret_share=None, status=TransactionStatus.PENDING_YOUR_APPROVAL)
    # add my data to the transaction
    my_wallet_user_data = sql_db_dal.get_my_wallet_user_data(wallet_id=wallet_id)
    if my_wallet_user_data is None:
        raise HTTPException(status_code=400, detail="cannot generate transaction, my data is not in the database")
    
    
    sql_db_dal.insert_transaction_user_data(transaction_id=transaction_id,user_matrix_id=user_id,user_index=my_wallet_user_data.user_index)
    
    transaction_json = MessageDTO(type=MessageType.TransactionRequest, data=transaction).model_dump_json()
    MatrixService.instance().send_message_to_wallet_room(room_id = wallet_id, message = transaction_json)
    transaction.status = TransactionStatus.PENDING_OTHERS_APPROVAL
    sql_db_dal.insert_new_transaction(transaction)
    return True

def respond_to_new_transaction(transaction_id : str,wallet_id : str, user_response : bool) -> bool:
    """
    * With respect to user response, updates provers list and transaction stage.
    * Saves in local_db the transaction stage
    * send transaction_response message in the corresponding room - only if approved. 
    """
    user_id = Context.matrix_user_id()
    transaction = sql_db_dal.get_transaction_by_id(transaction_id)
    if not user_response:
        sql_db_dal.update_transaction_status(transaction_id=transaction_id, status=TransactionStatus.DECLINED)
        print (f"user {user_id} rejects transaction {transaction_id}")
        return True
    else:
        my_wallet_user_data = sql_db_dal.get_my_wallet_user_data(wallet_id=wallet_id)
        if my_wallet_user_data is None:
            raise HTTPException(status_code=400, detail="cannot respond to transaction, my data is not in the database")
        transaction_response = TransactionResponseDTO(transaction_id=transaction_id, stage=transaction.status, response=user_response, approving_user_index=my_wallet_user_data.user_index, approving_user_matrix_id=user_id )
        sql_db_dal.insert_transaction_user_data(transaction_id=transaction.transaction_id,user_matrix_id=user_id,user_index=my_wallet_user_data.user_index)
        
        approved_transaction_json = MessageDTO(type = MessageType.TransactionResponse, data=transaction_response, sender_id=user_id,
                                                wallet_id=transaction.wallet_id, transaction_id=transaction.transaction_id, user_index=my_wallet_user_data.user_index).model_dump_json()
        MatrixService.instance().send_message_to_wallet_room(room_id=transaction.wallet_id, message= approved_transaction_json)   
        
        sql_db_dal.update_transaction_status(transaction_id=transaction_id, status=TransactionStatus.PENDING_OTHERS_APPROVAL)
        if TransactionService.threshold_reached( transaction.wallet_id, transaction.transaction_id):
            TransactionService.handle_reached_threshold_transaction(transaction=transaction, user_index=my_wallet_user_data.user_index)
        return True
    

def generate_unique_transaction_id():
    return "tx_" + str(uuid.uuid4())

# if __name__ == "__main__":
    
#     room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
#     transction_details = "Testing transction generation flow"
#     user_matrix_id = '@ron_test:matrix.org'
#     transaction_name = transction_details
#     #Why should we ever search for the existing transaction here?
#     existing_trans = sql_db_dal.get_transactions_by_wallet_id(room_id, should_convert_to_dto=True)
#     for trans in existing_trans:
#         approved = respond_to_new_transaction(user_id=user_matrix_id, transaction=trans,  user_response=True)
#     res = generate_transaction_and_send_to_wallet(user_matrix_id, room_id, transction_details, transaction_name)

