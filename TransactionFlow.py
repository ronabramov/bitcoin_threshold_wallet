from local_db import sql_db, sql_db_dal
from .models.transaction import Transaction as TransactionDTO
import uuid
import matrix_utils
from matrix_client.client import MatrixClient

def generate_transaction_signature(user_id, wallet_id, transaction_details, name, matrix_client : MatrixClient) -> bool:
    transaction_id = generate_unique_transaction_id()
    transaction = TransactionDTO(id= transaction_id, name=name, details=transaction_details, approvers="user_id", wallet_id=wallet_id)
    transaction.approve(user_id)
    insertion_succeded = sql_db_dal.insert_new_transaction(transaction)
    if not insertion_succeded:
        return False
    
    transaction_json = {
        "transaction_id": transaction_id,
        "wallet_id": wallet_id,
        "details": transaction_details,
        "approvers": [user_id]
    }
    
    matrix_utils.send_message_to_wallet_room(room_id = wallet_id, message = transaction_json, admin_user=None, admin_password=None, client=matrix_client)



def generate_unique_transaction_id():
    return "tx_" + str(uuid.uuid4())

if __name__ == "__main__":
    client = matrix_utils.create_matrix_cleint(matrix_user_id = "ron_test", matrix_user_password= "Roniparon32")
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    transction_details = "Testing transction generation flow"
    user_matrix_id = '@ron_test:matrix.org'
    transaction_name = transction_details
    res = generate_transaction_signature(user_matrix_id, room_id, transction_details, transaction_name, client)

