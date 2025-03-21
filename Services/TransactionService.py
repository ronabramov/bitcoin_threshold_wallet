from models.DTOs.transaction_dto import TransactionDTO
from models.transaction_status import TransactionStatus
from local_db import sql_db_dal
from local_db import sql_db
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from Services.Context import Context
from models.protocols.ShareShrinker import ShareShrinker
from ecdsa import curves
from APIs.Algorithm_Steps_Implementation.StepOne import StepOne_PrepareDataForMta
import time
def threshold_reached( wallet_id: int, transaction_id: str):
    try :
        wallet = sql_db_dal.get_wallet_by_id(wallet_id=wallet_id)
        transaction_user_data = sql_db_dal.get_all_transaction_user_data(transaction_id=transaction_id)
        return len(transaction_user_data) >= wallet.threshold
    except :
        raise FileNotFoundError(f"Failed finding wallet {wallet_id} in local_db")

def _approved_by_me(transaction_response: TransactionResponseDTO):
    ME = Context.matrix_user_id()
    transaction_user_data = sql_db_dal.get_all_transaction_user_data(transaction_id=transaction_response.transaction_id)
    # filter by ME with next()
    my_data = next((user_data for user_data in transaction_user_data if user_data.user_matrix_id == ME), None)
    return my_data is not None

def handle_incoming_transaction_response(transaction_response: TransactionResponseDTO):
    # get related transaction from local db
    local_transaction = sql_db_dal.get_transaction_by_id(transaction_response.transaction_id)
    print(f"Transaction response received: {transaction_response}")
    if local_transaction is None:
        # added to the db for future transaction request handling
        sql_db_dal.insert_transaction_response(transaction_response)
        return
    
    if(not _approved_by_me(transaction_response)):
        print(f"Transaction {transaction_response.transaction_id} not approved by me - skipping")
        return
    
    sql_db_dal.insert_transaction_user_data(transaction_id=transaction_response.transaction_id, 
                                            user_index=transaction_response.approving_user_index,
                                            user_matrix_id=transaction_response.approving_user_matrix_id)
    if (threshold_reached( local_transaction.wallet_id, local_transaction.transaction_id)):
        my_wallet_user_data = sql_db_dal.get_my_wallet_user_data(wallet_id=local_transaction.wallet_id)
        return handle_reached_threshold_transaction(transaction=local_transaction, user_index=my_wallet_user_data.user_index)
    
def handler_new_transaction(transaction: TransactionDTO):
    local_transaction = sql_db_dal.get_transaction_by_id(transaction.id)
    if local_transaction is None:
        sql_db_dal.insert_new_transaction(transaction)
        # User need to fetch the transaction from local db and display it in the UI.
        # check past transaction response in the db:
        past_transaction_responses = sql_db_dal.get_transaction_responses_by_transaction_id(transaction.id)
        for response in past_transaction_responses:
            handle_incoming_transaction_response(response)
    else:
        print(f"Transaction {transaction.id} already exists in the local db")
    return

def handle_reached_threshold_transaction(transaction : sql_db.Transaction, user_index: int) -> bool: 
    sql_db_dal.update_transaction_status(transaction_id=transaction.transaction_id, status=TransactionStatus.PROCESSING)
    wallet = sql_db_dal.get_wallet_by_id(transaction.wallet_id)
    user_secret_signature_data = wallet.get_room_secret_user_data()
    approvers_indexes = [participating_user.user_index for participating_user in sql_db_dal.get_all_transaction_user_data(transaction_id=transaction.transaction_id)]
    
    curve = curves.curve_by_name(wallet.curve_name)
    shrinker = ShareShrinker(q= curve.order, i = user_index, S=approvers_indexes, x_i=user_secret_signature_data.user_evaluation)
    shrunken_secret = shrinker.compute_new_share()
    
    sql_db_dal.insert_transaction_shrunken_secret(transaction_id=transaction.transaction_id, shrunken_secret_share=shrunken_secret)
    
    successeded_stage_one = StepOne_PrepareDataForMta.execute(wallet=wallet)
    return successeded_stage_one
