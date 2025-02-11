from local_db import sql_db_dal
from models.transaction_dto import TransactionDTO as TransactionDTO
from models.message_dto import MessageDTO as MessageWrapper
from models.transaction_status import TransactionStatus
from models.transaction_response import TransactionResponse
import uuid
from Services.MatrixService import MatrixService


"""
This is the APIs the controller should reach for any transaction service
Methods:
1. generate_transaction_and_send_to_wallet
2. respond_to_new_transaction
"""
def generate_transaction_and_send_to_wallet(user_id, wallet_id, transaction_details, name) -> bool:
    """
    * Generate new transaction
    * Saves transaction in local_db 
    * Send to corresponding wallet.

    Return True iff all stages done successfuly.  
    """
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details, wallet_id=wallet_id)
    transaction.approve(user_id)
    insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
    if not insertion_succeded:
        return False
    
    # Use the Message DTO
    transaction_json = MessageWrapper(type='transaction_request', data=transaction).model_dump_json()
    message = MessageWrapper.model_validate_json(transaction_json)
    return MatrixService.instance().send_message_to_wallet_room(room_id = wallet_id, message = transaction_json)


def respond_to_new_transaction(user_id : str, transaction : TransactionDTO, user_response : bool) -> bool:
    """
    * With respect to user response, updates provers list and transaction stage.
    * Saves in local_db the transaction stage
    * send transaction_response message in the corresponding room - only if approved. 
    """
    if not user_response:
        print (f"user {user_id} rejects transaction {transaction.id}")
        return True
    else:
        transaction.approve(user_id)
        threshold_achieved = check_threshold(transaction)
        if threshold_achieved :
            transaction.stage = TransactionStatus.THRESHOLD_ACHIEVED ######SHOULD HAVE OBJECT AND SEND MESSAGE AS MESSAGE WRAPPER OVER THAT OBJECT
        transaction_response = TransactionResponse(transaction_id=transaction.id, stage=transaction.stage, response=user_response, approvers_counter=transaction.approvers_counter, approvers=transaction.approvers)
        insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
        if not insertion_succeded:
            return False
        
        # Use the Message DTO
        approved_transaction_json = MessageWrapper(type = TransactionResponse.get_type(), data=transaction_response).model_dump_json()
        message = MessageWrapper.model_validate_json(approved_transaction_json)
        return MatrixService.instance().send_message_to_wallet_room(room_id=transaction.wallet_id, message= approved_transaction_json)   
        
def check_threshold(transaction : TransactionDTO):
    try :
        wallet = sql_db_dal.get_wallet_by_id(wallet_id= transaction.wallet_id)
        return transaction.approvers_counter >= wallet.threshold
    except :
        return False

def generate_unique_transaction_id():
    return "tx_" + str(uuid.uuid4())

if __name__ == "__main__":
    
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    transction_details = "Testing transction generation flow"
    user_matrix_id = '@ron_test:matrix.org'
    transaction_name = transction_details
    #Why should we ever search for the existing transaction here?
    existing_trans = sql_db_dal.get_transactions_by_wallet_id(room_id, should_convert_to_dto=True)
    for trans in existing_trans:
        approved = respond_to_new_transaction(user_id=user_matrix_id, transaction=trans,  user_response=True)
    res = generate_transaction_and_send_to_wallet(user_matrix_id, room_id, transction_details, transaction_name)

