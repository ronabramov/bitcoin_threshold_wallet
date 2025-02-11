from local_db import sql_db_dal
from models.transaction_dto import TransactionDTO as TransactionDTO
from models.transaction_status import TransactionStatus
import uuid
from MatrixService import MatrixService

def generate_transaction_and_send_to_wallet(user_id, wallet_id, transaction_details, name) -> bool:
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details, wallet_id=wallet_id)
    transaction.approve(user_id)
    insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
    if not insertion_succeded:
        return False
    
    transaction_json = transaction.model_dump_json()
    message = {
        "msgtype": "m.text",
        "content": transaction_json 
    }

    des = TransactionDTO.model_validate_json(transaction_json)
    return MatrixService.instance().send_message_to_wallet_room(room_id = wallet_id, message = message)

def check_threshold(transaction : TransactionDTO):
    wallet = sql_db_dal.get_wallet_by_id(wallet_id= transaction.wallet_id)
    return transaction.approvers_counter >= wallet.threshold

def approve_new_transaction(user_id : str, transaction : TransactionDTO, user_accepted : bool) -> bool:
    if not user_accepted:
        print (f"user {user_id} rejects transaction {transaction.id}")
        return True
    else:
        transaction.approve(user_id)
        threshold_achieved = check_threshold(transaction)
        if threshold_achieved :
            transaction.stage = TransactionStatus.THRESHOLD_ACHIEVED

        insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
        if not insertion_succeded:
            return False
        approved_transaction_json = {
        "body": f"Transaction accepted by {user_id}",
        "transaction_id": transaction.id,
        "approvers": transaction.approvers,
        "stage" : transaction.stage.value
        }
        message = {
        "msgtype": "m.text",
        "content": approved_transaction_json 
        }
        return MatrixService.instance().send_message_to_wallet_room(room_id=transaction.wallet_id, message= message)   
        

def generate_unique_transaction_id():
    return "tx_" + str(uuid.uuid4())

if __name__ == "__main__":
    
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    transction_details = "Testing transction generation flow"
    user_matrix_id = '@ron_test:matrix.org'
    transaction_name = transction_details
    #Why should we ever search for the existing transaction here?
    # existing_trans = sql_db_dal.get_transactions_by_wallet_id(room_id, should_convert_to_dto=True)
    # for trans in existing_trans:
    #     approved = approve_new_transaction(user_id=user_matrix_id, transaction=trans,  user_accepted=True)
    res = generate_transaction_and_send_to_wallet(user_matrix_id, room_id, transction_details, transaction_name)

