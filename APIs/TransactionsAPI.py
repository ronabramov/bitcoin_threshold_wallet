from local_db import sql_db_dal
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.message_dto import MessageDTO
from models.DTOs.MessageType import MessageType
from models.DTOs.wallet_dto import WalletDto
from models.transaction_status import TransactionStatus
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.models import user_public_share
from APIs.Algorithm_Steps_Implementation.user_transaction_configuration_handler import UserTransactionConfigurationHandler as ConfigHandler
import uuid
from Services.MatrixService import MatrixService
from Services import TransactionService
from Services.Context import Context
"""
This is the APIs the controller should reach for any transaction service
Methods:
1. generate_transaction_and_send_to_wallet
2. respond_to_new_transaction
"""
def generate_transaction_and_send_to_wallet( wallet_id, transaction_details, name) -> bool:
    """
    * Generate new transaction
    * Saves transaction in local_db 
    * Send to corresponding wallet.

    Return True iff all stages done successfuly.  
    """
    user_id = Context.matrix_user_id()
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details, wallet_id=wallet_id)
    transaction.approve(user_id)
    insertion_succeeded = sql_db_dal.insert_new_transaction(transaction)
    if not insertion_succeeded:
        return False
    # transaction request message is handled as a transaction message
    transaction_json = MessageDTO(type=MessageType.TransactionRequest, data=transaction).model_dump_json()
    return MatrixService.instance().send_message_to_wallet_room(room_id = wallet_id, message = transaction_json)

def respond_to_new_transaction(transaction : TransactionDTO, user_response : bool) -> bool:
    """
    * With respect to user response, updates provers list and transaction stage.
    * Saves in local_db the transaction stage
    * send transaction_response message in the corresponding room - only if approved. 
    """
    user_id = Context.matrix_user_id()
    if not user_response:
        print (f"user {user_id} rejects transaction {transaction.id}")
        return True
    else:
        transaction.approve(user_id)
        threshold_achieved = TransactionService.threshold_reached(transaction.approvers_counter, transaction.wallet_id)
        transaction_response = TransactionResponseDTO(transaction_id=transaction.id, stage=TransactionStatus.THRESHOLD_ACHIEVED if threshold_achieved  else transaction.stage, response=user_response, approvers_counter=transaction.approvers_counter, approvers=transaction.approvers)
        insertion_succeeded = sql_db_dal.insert_new_transaction(transaction)
        
        if not insertion_succeeded:
            return False
        
        if threshold_achieved:    
            wallet = sql_db_dal.get_wallet_by_id(transaction.wallet_id)
            handle_reached_threshold_transaction(transaction=transaction, wallet=wallet)
            
        approved_transaction_json = MessageDTO(type = MessageType.TransactionResponse, data=transaction_response).model_dump_json()
        return MatrixService.instance().send_message_to_wallet_room(room_id=transaction.wallet_id, message= approved_transaction_json)   

def handle_reached_threshold_transaction(transaction : TransactionDTO, wallet: WalletDto) -> bool: #####RE VISIT
    config_handler = ConfigHandler()
    _, transaction_room_id, public_key = config_handler.define_transaction_user_config_and_send_shares(transaction=transaction, wallet=wallet) #Consider passing Curve.
    public_keys_message = MessageDTO(type = MessageType.UserPublicShare, data=public_key).model_dump_json()
    return MatrixService.instance().send_message_to_wallet_room(room_id=transaction_room_id, message=public_keys_message)
    

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

