from local_db import sql_db_dal
from models.transaction_dto import TransactionDTO as TransactionDTO
from models.transaction_status import TransactionStatus
import uuid
import matrix_utils
from matrix_client.client import MatrixClient

def generate_transaction(user_id, wallet_id, transaction_details, name, matrix_client : MatrixClient) -> bool:
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details, wallet_id=wallet_id)
    transaction.approve(user_id)
    insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
    if not insertion_succeded:
        return False
    
    transaction_json = {
        "body": f"New transaction request by {user_id}",
        "transaction_id": transaction_id,
        "wallet_id": wallet_id,
        "details": transaction_details,
        "approvers": [user_id]
    }
    message = {
        "msgtype": "m.text",
        "content": transaction_json 
    }
    return matrix_utils.send_message_to_wallet_room(room_id = wallet_id, message = message, admin_user=None, admin_password=None, client=matrix_client)

def check_threshold(transaction : TransactionDTO):
    wallet = sql_db_dal.get_wallet_by_id(wallet_id= transaction.wallet_id)
    return transaction.approvers_counter >= wallet.threshold

def approve_new_transaction(user_id : str, transaction : TransactionDTO, matrix_client : MatrixClient, user_accepted : bool) -> bool:
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
        return matrix_utils.send_message_to_wallet_room(room_id=transaction.wallet_id, message= message, client= matrix_client)   
        

def generate_unique_transaction_id():
    return "tx_" + str(uuid.uuid4())

if __name__ == "__main__":
    client = matrix_utils.create_matrix_cleint(matrix_user_id = "ron_test", matrix_user_password= "Roniparon32")
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    transction_details = "Testing transction generation flow"
    user_matrix_id = '@ron_test:matrix.org'
    transaction_name = transction_details
    existing_trans = sql_db_dal.get_transactions_by_wallet_id(room_id, should_convert_to_dto=True)
    for trans in existing_trans:
        approved = approve_new_transaction(user_id=user_matrix_id, transaction=trans, matrix_client=client, user_accepted=True)
    res = generate_transaction(user_matrix_id, room_id, transction_details, transaction_name, client)

