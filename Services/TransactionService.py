from models.DTOs.transaction_dto import TransactionDTO
from models.transaction_status import TransactionStatus
from local_db import sql_db_dal
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from Services.Context import Context
from APIs.RoomManagementAPI import MatrixService
from models.DTOs.message_dto import MessageDTO, MessageType
from APIs.Algorithm_Steps_Implementation.user_transaction_configuration_handler import UserTransactionConfigurationHandler as ConfigHandler
from models.DTOs.wallet_dto import WalletDto
# TODO: change to the user's matrix id
# ME = "@my_user_id:matrix.org"


def threshold_reached(approvers_counter: int, wallet_id: int):
    try :
        wallet = sql_db_dal.get_wallet_by_id(wallet_id=wallet_id)
        return approvers_counter >= wallet.threshold
    except :
        raise FileNotFoundError(f"Failed finding wallet {wallet_id} in local_db")

def _approved_by_me(transaction_response: TransactionResponseDTO):
    ME = Context.matrix_user_id()
    return ME in transaction_response.approvers

def handle_incoming_transaction_response(transaction_response: TransactionResponseDTO):
    # get related transaction from local db
    local_transaction = sql_db_dal.get_transaction_by_id(
        transaction_response.transaction_id
    )
    print(f"Transaction response received: {transaction_response}")
    if local_transaction is None:
        # added to the db for future transaction request handling
        sql_db_dal.insert_transaction_response(transaction_response)
        return
    
    local_transaction_dto = sql_db_dal.map_transaction_to_dto(local_transaction)
    if(not _approved_by_me(transaction_response)):
        print(f"Transaction {transaction_response.transaction_id} not approved by me - skipping")
        return
    
    if (threshold_reached(transaction_response.approvers_counter, local_transaction_dto.wallet_id)):
        local_transaction_dto.stage = TransactionStatus.THRESHOLD_ACHIEVED
        sql_db_dal.update_transaction(local_transaction_dto)
        
        wallet = sql_db_dal.get_wallet_by_id(local_transaction_dto.wallet_id)
        handle_reached_threshold_transaction(transaction=local_transaction_dto, wallet=wallet)
        return
    
    # threshold not reached
    local_transaction_dto = _merge_transactions(transaction_response, local_transaction_dto)
    sql_db_dal.update_transaction(local_transaction_dto)
        

def _merge_transactions(
    self,
    incoming_transaction: TransactionResponseDTO,
    local_transaction: TransactionDTO,
):
    local_approvers = local_transaction.approvers.split(",")
    incoming_approvers = incoming_transaction.approvers.split(",")
    
    local_approvers_counter = local_transaction.approvers_counter
    incoming_approvers_counter = incoming_transaction.approvers_counter
    
    merged_approvers = set(local_approvers + incoming_approvers)
    incoming_transaction.approvers = max(
        local_approvers_counter, incoming_approvers_counter
    )
    local_transaction.approvers = ",".join(merged_approvers)
    local_transaction.stage = max(local_transaction.stage, incoming_transaction.stage)
    return local_transaction


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

def handle_reached_threshold_transaction(transaction : TransactionDTO, wallet: WalletDto) -> bool: #####RE VISIT
    config_handler = ConfigHandler()
    _, transaction_room_id, public_key = config_handler.define_transaction_user_config_and_send_shares(transaction=transaction, wallet=wallet) #Consider passing Curve.
    public_keys_message = MessageDTO(type = MessageType.UserPublicShare, data=public_key).model_dump_json()
    return MatrixService.instance().send_message_to_wallet_room(room_id=transaction_room_id, message=public_keys_message)