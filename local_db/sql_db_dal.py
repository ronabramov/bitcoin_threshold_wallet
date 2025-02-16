from local_db import sql_db
from typing import Dict, Optional, List
from DTOs.transaction_dto import TransactionDTO as TransactionDTO
from models.transaction_status import TransactionStatus
from models.models import room_public_user_data, user_public_share
from enum import Enum

def get_transaction_room_data_by_trans_id(transaction_id : str):
    try:
        transaction_room_data = sql_db.session.query(sql_db.Room_User_Data).filter(
                                                     sql_db.Room_User_Data.transaction_id == transaction_id).first()
        if not transaction_room_data:
            print(f"Couldn't find room_transaction_data for transaction {transaction_id}")
            raise FileNotFoundError(f"Couldn't find room_transaction_data for transaction {transaction_id}")
        return transaction_room_data.transaction_id, transaction_room_data.room_id, transaction_room_data.curve_name
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction-room data for transaction {transaction_id}", e)

def get_transaction_participating_users_data_by_trans_id(transaction_id : str) -> dict[int, room_public_user_data]:
    try:
        transaction_room_data = sql_db.session.query(sql_db.Room_User_Data).filter(
                                                     sql_db.Room_User_Data.transaction_id == transaction_id).first()
        if not transaction_room_data:
            print(f"Couldn't find room_transaction_data for transaction {transaction_id}")
            raise FileNotFoundError(f"Couldn't find room_transaction_data for transaction {transaction_id}")
        return transaction_room_data.list_participants()
    except Exception as e:
        print(f"There was and error while trying to retrieve users data for transaction {transaction_id}", e)

def get_user_by_email(user_email : str) -> sql_db.User :
    try:
        user = sql_db.session.query(sql_db.User).filter(sql_db.User.email == user_email).first()
        if not user :
            print (f"Couldn't find user with email {user_email}")
            raise FileNotFoundError(f"User with email {user_email} couldn't be found")
        return user
    except Exception as e:
        print(f"There was and error while trying to retrieve user {user_email}", e)

def get_friend_by_email(email : str) -> sql_db.Friend:
    try:
        friend = sql_db.session.query(sql_db.Friend).filter(sql_db.Friend.email == email).first()
        if not friend :
            print (f"Couldn't find friend with email {email}")
            raise FileNotFoundError(f"Friend with email {email} couldn't be found")
        return friend
    except Exception as e:
        print(f"There was and error while trying to retrieve friend with email :  {email}", e)


def get_all_user_friends() -> List[sql_db.User]:
    users = sql_db.session.query(sql_db.Friend).all()
    return users

def get_wallet_by_id(wallet_id : str) -> sql_db.Wallet:
    try:
        wallet = sql_db.session.query(sql_db.Wallet).filter(sql_db.Wallet.wallet_id == wallet_id).first()
        if not wallet :
            print (f"Wallet with Id : {wallet_id} couldn't be found")
            raise FileNotFoundError(f"wallet with Id : {wallet_id} couldn't be found")
        return wallet
    except Exception as e:
        print(f"There was and error while trying to retrieve wallet {wallet_id}", e)

def get_transaction_by_id(transaction_id : str) -> sql_db.Transaction:
    try:
        transaction = sql_db.session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
        if not transaction :
            print (f"Couldn't find transaction with id : {transaction_id}")
            raise FileNotFoundError(f"Transaction with id {transaction_id} couldn't be found")
        return transaction
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction {transaction_id}", e)

def get_transactions_by_wallet_id(wallet_id : str, should_convert_to_dto = False):
    try:
        transactions = sql_db.session.query(sql_db.Transaction).filter(sql_db.Transaction.wallet_id == wallet_id).all()
        if not transactions :
            print (f"Couldn't find transaction for wallet  : {wallet_id}")
            raise FileNotFoundError(f"Transaction with wallet id  {wallet_id} couldn't be found")
        if should_convert_to_dto:
            dto_list =  [map_transaction_to_dto(transaction) for transaction in transactions]
            return dto_list
        return transactions
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction for wallet {wallet_id}", e)

def insert_new_transaction(transaction : TransactionDTO) -> bool:
    try:
        transaction_to_insert = sql_db.Transaction.from_dto(transaction_dto=transaction)
        sql_db.session.add(transaction_to_insert)
        sql_db.session.commit()
        print(f"Succesffully inserted transaction {transaction.id}")
        return True
    except Exception as e:
        print(f'failed to insert transaction {transaction.id} to db.', e)
        return False
    
def insert_transaction_room(
        self, transaction_id: str, room_id: str, curve_name: str, participants_dict: dict[int, room_public_user_data]
    ) -> sql_db.Room_User_Data:
        """
        Inserts a new transaction room entry into the database.

        :param transaction_id: Unique transaction identifier.
        :param room_id: Matrix room ID.
        :param curve_name: Cryptographic curve used.
        :param participants_dict: Dictionary of index -> public_user_data objects.
        :return: The created Transaction_Room object.
        """
        participants_data = {str(index): user.to_dict() for index, user in participants_dict.items()}

        new_transaction_room_data = sql_db.Room_User_Data(
            transaction_id=transaction_id,
            room_id=room_id,
            curve_name=curve_name,
            participants_data=participants_data
        )

        self.session.add(new_transaction_room_data)
        self.session.commit()
        return new_transaction_room_data

def insert_new_wallet(wallet : sql_db.Wallet) -> bool:
    try:
        sql_db.session.add(wallet)
        sql_db.session.commit()
        print(f"Successffuly inserted wallet {wallet.wallet_id} to db")
        return True
    except Exception as e:
        print(f"Failed to insert wallet {wallet.wallet_id}", e)
        return False

def inser_new_room_user(wallet_id : str, user_index : int, user_matrix_id : str, user_public_keys : user_public_share):
    try:
        rooom_user_data = sql_db.Room_User_Data(user_index = user_index, user_matrix_id=user_matrix_id,
                                                 user_public_keys_data = user_public_keys.to_dict(), wallet_id=wallet_id)
        sql_db.session.add(rooom_user_data)
        sql_db.session.commit()
        print(f"Successffuly inserted room's user data for user {user_matrix_id} in wallet {wallet_id} to db")
        return True
    except Exception as e:
        print(f"Failed to insert user {user_matrix_id} into wallet {wallet_id}", e)
        return False

def map_transaction_to_dto(transaction : sql_db.Transaction) -> TransactionDTO: #The transaction db must contain all properties of DTO. name is irrelevant?
    transaction_dto = transaction_dto = TransactionDTO(
    id=transaction.transaction_id,  
    name="", 
    details=transaction.details, 
    wallet_id=transaction.wallet_id
    )
    transaction_dto.approvers = transaction.approvers
    transaction_dto.approvers_counter = transaction.approvals_counter
    transaction_dto.stage = TransactionStatus[transaction.status.upper()]
    return transaction_dto
