from local_db import sql_db
from local_db.sql_db import DB
from typing import List
from models.DTOs.transaction_dto import TransactionDTO as TransactionDTO
from models.transaction_status import TransactionStatus
from models.models import  user_public_share, wallet_key_generation_share
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from Services.Context import Context

def get_user_by_email(user_email : str) -> sql_db.User :
    try:
        user = DB.session().query(sql_db.User).filter(sql_db.User.email == user_email).first()
        if not user :
            print (f"Couldn't find user with email {user_email}")
            raise FileNotFoundError(f"User with email {user_email} couldn't be found")
        return user
    except Exception as e:
        print(f"There was and error while trying to retrieve user {user_email}", e)

def get_friend_by_email(email : str) -> sql_db.Friend:
    try:
        friend = DB.session().query(sql_db.Friend).filter(sql_db.Friend.email == email).first()
        if not friend :
            print (f"Couldn't find friend with email {email}")
            raise FileNotFoundError(f"Friend with email {email} couldn't be found")
        return friend
    except Exception as e:
        print(f"There was and error while trying to retrieve friend with email :  {email}", e)


def get_all_user_friends() -> List[sql_db.User]:
    users = DB.session().query(sql_db.Friend).all()
    return users

def get_wallet_by_id(wallet_id : str) -> sql_db.Wallet:
    try:
        wallet = DB.session().query(sql_db.Wallet).filter(sql_db.Wallet.wallet_id == wallet_id).first()
        if not wallet :
            print (f"Wallet with Id : {wallet_id} couldn't be found")
            raise FileNotFoundError(f"wallet with Id : {wallet_id} couldn't be found")
        return wallet
    except Exception as e:
        print(f"There was and error while trying to retrieve wallet {wallet_id}", e)

def get_transaction_by_id(transaction_id : str) -> sql_db.Transaction:
    try:
        transaction = DB.session().query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
        if not transaction :
            print (f"Couldn't find transaction with id : {transaction_id}")
            return None
        return transaction
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction {transaction_id}", e)

def get_transactions_by_wallet_id(wallet_id : str, should_convert_to_dto = False):
    try:
        transactions = DB.session().query(sql_db.Transaction).filter(sql_db.Transaction.wallet_id == wallet_id).all()
        if not transactions :
            print (f"Couldn't find transaction for wallet  : {wallet_id}")
            raise FileNotFoundError(f"Transaction with wallet id  {wallet_id} couldn't be found")
        if should_convert_to_dto:
            dto_list =  [map_transaction_to_dto(transaction) for transaction in transactions]
            return dto_list
        return transactions
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction for wallet {wallet_id}", e)

def get_signature_shares_by_wallet(wallet_id: str) -> list[wallet_key_generation_share]:
    """
    Retrieves all signature shares for a given wallet.

    :param session: SQLAlchemy session.
    :param wallet_id: Wallet ID to fetch signature shares for.
    :return: List of `user_key_generation_share` objects.
    """
    shares = DB.session().query(sql_db.WalletSignatureSharesData).filter_by(wallet_id=wallet_id).all()
    return [wallet_key_generation_share.from_dict(share.share_data) for share in shares]


def insert_signature_share(wallet_id: str, share_data: wallet_key_generation_share) -> bool:
    # TODO: check issue here
    share_data = share_data[1]
    share_index = share_data.target_user_index
    try:
        share_entry = sql_db.WalletSignatureSharesData(
            share_id = f'{wallet_id}_{share_index}',
            share_index=share_index,
            share_data=share_data.to_dict(),
            wallet_id=wallet_id
        )
        DB.session().add(share_entry)
        DB.session().commit()
        print(f"Successfully inserted signature share {share_index} for wallet {wallet_id}.")
        return True
    
    except Exception as e:
        DB.session().rollback()
        print(f"Failed to insert signature share {share_index} for wallet {wallet_id}: {e}")
        return False


def insert_multiple_signature_shares(wallet_id: str, shares: list[wallet_key_generation_share]) -> bool:
    success = True
    for share in enumerate(shares):
        # TODO: check issue here
        result = insert_signature_share(wallet_id, share_data=share)
        if not result:
            success = False
    return success


def insert_new_transaction(transaction : TransactionDTO) -> bool:
    try:
        transaction_to_insert = sql_db.Transaction.from_dto(transaction_dto=transaction)
        DB.session().add(transaction_to_insert)
        DB.session().commit()
        print(f"Successfully inserted transaction {transaction.id}")
        return True
    except Exception as e:
        print(f'failed to insert transaction {transaction.id} to db.', e)
        return False

def update_transaction(transaction : TransactionDTO) -> bool:
    try:
        # TODO - add from_dto (it is not working as you see)
        transaction_to_update = sql_db.Transaction.from_dto(transaction_dto=transaction)
        DB.session().query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction.id).update(transaction_to_update)
        DB.session().commit()
        print(f"Successfully updated transaction {transaction.id}")
        return True
    except Exception as e:
        print(f'failed to update transaction {transaction.id} to db.', e)
        return False

def insert_new_wallet(wallet : sql_db.Wallet) -> bool:
    try:
        DB.session().add(wallet)
        DB.session().commit()
        print(f"Successfully inserted wallet {wallet.wallet_id} to db")
        return True
    except Exception as e:
        print(f"Failed to insert wallet {wallet.wallet_id}", e)
        return False

def insert_my_wallet_user_data(wallet_id : str,  user_public_keys : user_public_share):
    insert_new_wallet_user_data(wallet_id=wallet_id, user_index=user_public_keys.user_index, user_matrix_id=Context.matrix_user_id(), user_public_keys=user_public_keys)

def get_my_wallet_user_data(wallet_id : str) -> sql_db.WalletUserData:
    return DB.session().query(sql_db.WalletUserData).filter(sql_db.WalletUserData.wallet_id == wallet_id, sql_db.WalletUserData.user_matrix_id == Context.matrix_user_id()).first()


# TODO: maybe remove matrix id and index as parameters since we get them from the user_public_keys
def insert_new_wallet_user_data(wallet_id : str, user_index : int, user_matrix_id : str, user_public_share : user_public_share):
    try:
        # TODO: add a check if the user share already exists in the db
        room_user_data = sql_db.WalletUserData(user_index = user_index, user_matrix_id=user_matrix_id,
                                                 user_public_keys_data = user_public_share.to_dict(), wallet_id=wallet_id)
        DB.session().add(room_user_data)
        DB.session().commit()
        print(f"Successfully inserted room's user data for user {user_matrix_id} in wallet {wallet_id} to db")
        return True
    except Exception as e:
        print(f"Failed to insert user {user_matrix_id} into wallet {wallet_id}", e)
        return False

def insert_new_friend(user_email : str, user_matrix_id : str) -> bool:
    friend_db_object = sql_db.Friend(email=user_email, matrix_id = user_matrix_id)
    try:
        DB.session().add(friend_db_object)
        DB.session().commit()
        return True
    except Exception as e:
        print(f"Failed to inserting user {user_matrix_id} into Friends table", e)
        DB.session().rollback()
        return False

def map_transaction_to_dto(transaction : sql_db.Transaction) -> TransactionDTO:
    transaction_dto = transaction_dto = TransactionDTO(
    id=transaction.transaction_id,  
    name="", 
    details=transaction.details, 
    wallet_id=transaction.wallet_id
    )
    transaction_dto.stage = TransactionStatus[transaction.status]
    return transaction_dto

def update_signature_share(wallet_id : str, share : wallet_key_generation_share) -> bool:
    try:
        share_db_object = DB.session().query(sql_db.WalletSignatureSharesData).filter(
            sql_db.WalletSignatureSharesData.share_index == share.target_user_index, 
            sql_db.WalletSignatureSharesData.wallet_id == wallet_id).first()
        share_db_object.user_matrix_id = share.target_user_matrix_id
        share_db_object.share_data = share.to_dict()
        DB.session().commit()
        return True
    except Exception as e:
        print(f"Failed to update signature share for wallet {wallet_id}", e)
        
def get_transaction_responses_by_transaction_id(transaction_id : str) -> sql_db.TransactionResponse:
    try:
        return  DB.session().query(sql_db.TransactionResponse).filter(sql_db.TransactionResponse.transaction_id == transaction_id).all()
    except Exception as e:
        print(f"Failed to get transaction response for transaction {transaction_id}", e)
        return None

def insert_transaction_response(transaction_response : TransactionResponseDTO) -> bool:
    try:
        transaction_response_to_insert = sql_db.TransactionResponse.from_dto(transaction_response_dto=transaction_response)
        DB.session().add(transaction_response_to_insert)
        DB.session().commit()
        print(f"Successfully inserted transaction response {transaction_response.transaction_id}")
        return True
    except Exception as e:
        print(f"Failed to insert transaction response {transaction_response.transaction_id}", e)
        return False
    
def insert_transaction_secret(transaction_id : str, shrunken_secret_share : int) -> bool:
    try:
        transaction = DB.session().query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
        if not transaction:
            print(f"Transaction {transaction_id} not found")
            return False
        transaction.shrunken_secret_share = shrunken_secret_share
        DB.session().commit()
        return True
    except Exception as e:
        print(f"Failed to insert transaction secret {transaction_id}", e)
        DB.session().rollback()
        return False

def get_transaction_secret(transaction_id : str):
    """
    Do not broadcast!
    """
    try:
        transaction = DB.session().query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
        return transaction.shrunken_secret_share
    except Exception as e:
        print(f"Failed to get transaction secret {transaction_id}", e)
        return None

def insert_transaction_user_data(transaction_id : str, user_index : int, user_matrix_id : str) -> bool:
    try:
        transaction_user_data = sql_db.TransactionUserData(transaction_id=transaction_id, user_index=user_index, user_matrix_id=user_matrix_id)
        DB.session().add(transaction_user_data)
        DB.session().commit()
        return True
    except Exception as e:
        print(f"Failed to insert transaction user data {transaction_id}", e)
        return False

def get_transaction_user_data_by_index(transaction_id : str, user_index : int) -> sql_db.TransactionUserData:
    return DB.session().query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id, sql_db.TransactionUserData.user_index == user_index).first()

def get_transaction_user_data_by_matrix_id(transaction_id : str, user_matrix_id : str) -> sql_db.TransactionUserData:
    return DB.session().query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id, sql_db.TransactionUserData.user_matrix_id == user_matrix_id).first()


def get_all_transaction_user_data(transaction_id : str) -> List[sql_db.TransactionUserData]:
    return DB.session().query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id).all()