import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models.models import (
    user_public_share,
    user_secret_signature_share,
    wallet_key_generation_share,
)
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.transaction_response_dto import TransactionResponseDTO
import json
import Config
import uuid

from Services.Context import Context

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    homeserver_url = Column(String, nullable=True)
    homeserver_login = Column(String, nullable=True)
    homeserver_password = Column(String, nullable=True)

class Friend(Base):
    __tablename__ = "friends"
    email = Column(String, primary_key=True, nullable=False)
    matrix_id = Column(String, primary_key=False, nullable=False)


class Wallet(Base):
    __tablename__ = "wallets"
    wallet_id = Column(
        String, primary_key=True, nullable=False
    )  # This will be the room Id.
    threshold = Column(Integer, nullable=False)
    max_num_of_users = Column(Integer, nullable=False)
    users = Column(
        Text, nullable=True
    )  # @alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    configuration = Column(Text, nullable=True)  # User secret (real type is user_secret_signature_share)
    curve_name = Column(Text, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")
    users_data = relationship("Room_User_Data", back_populates="wallet")
    signature_shares = relationship(
        "Room_Signature_Shares_Data", back_populates="wallet"
    )

    def set_room_secret_user_data(self, data: user_secret_signature_share):
        self.configuration = data.model_dump_json()

    def get_room_secret_user_data(self):
        if self.configuration:
            data = json.loads(self.configuration)
            return user_secret_signature_share.model_validate(data)
        return None


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, nullable=False)
    details = Column(Text, nullable=True)
    approvers = Column(Text, nullable=True)
    approvals_counter = Column(Integer, nullable=True)
    status = Column(Integer, nullable=True)
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")
    shrunken_secret_share = Column(Integer, nullable=True)


# check every transaction user changes - should we change simething in this table?
class TransactionUserData(Base):
    __tablename__ = "transaction_user_data"
    # id with uuid default val
    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    user_matrix_id = Column(String, primary_key=True, nullable=False)
    user_index = Column(Integer, primary_key=True, nullable=False)
    mta_data = Column(JSON, nullable=True) 
    
    def add_mta_data(self, mta_info: dict):
        self.mta_data = mta_info

    def get_mta_data(self) -> dict:
        return self.mta_data

    def remove_mta_data(self):
        self.mta_data = {}


    @classmethod
    def from_dto(cls, transaction_dto: "TransactionDTO"):
        # Create a new instance and populate it with the DTO values
        transaction = cls(
            transaction_id=transaction_dto.id,
            details=transaction_dto.details,
            approvers=transaction_dto.approvers,
            approvals_counter=transaction_dto.approvers_counter,
            wallet_id=transaction_dto.wallet_id,
            status=transaction_dto.stage.value,
        )
        return transaction


class WalletUserData(Base):
    """
    One per user X Wallet
    """

    __tablename__ = "wallet_user_data"

    user_index = Column(Integer, primary_key=True, nullable=False)
    user_matrix_id = Column(String, primary_key=True, nullable=False)
    user_public_keys_data = Column(JSON, nullable=False, default={})  # Paillier Public key and Modulus data - that is the user_public_share
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="users_data")


class Wallet_Signature_Shares_Data(Base):
    __tablename__ = "room_signature_shares_data"
    share_id = Column(String, primary_key=True, nullable=False)
    share_index = Column(Integer, primary_key=False, nullable=False)
    user_matrix_id = Column(String,primary_key=False, nullable=True)
    share_data = Column(
        JSON, nullable=False, default={}
    )  # data of to dict/from_dict of key_generation_share.
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="signature_shares")

    def get_signature_share(self, user_index: int) -> wallet_key_generation_share:
        return wallet_key_generation_share.from_dict(self.share_data)

class TransactionResponse(Base):
    __tablename__ = "transaction_responses"
    id = Column(Integer, primary_key=True, nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    stage = Column(Integer, nullable=False)
    response = Column(Boolean, nullable=False)
    approvers_counter = Column(Integer, nullable=False)
    approvers = Column(String, nullable=True)
    
    def from_dto(cls, transaction_response_dto: TransactionResponseDTO):
        return cls(
            transaction_id=transaction_response_dto.transaction_id,
            stage=transaction_response_dto.stage,
            response=transaction_response_dto.response,
            approvers_counter=transaction_response_dto.approvers_counter,
            approvers=transaction_response_dto.approvers
        )

def create_db_if_not_exists(db_file_name): 
    current_path = os.path.dirname(
            os.path.abspath(__file__)
        )
    abs_path = os.path.join(current_path, db_file_name)
    engine = create_engine(f"sqlite:///{abs_path}")
    if not os.path.exists(abs_path):    
        Base.metadata.create_all(engine)
    # Session maker
    Session = sessionmaker(bind=engine)
    # this is the session that will be used to interact with the database
    session = Session()
    return session


class DB():
    sessions = {
        Config.Test.User1.matrix_id: create_db_if_not_exists(Config.DB_FILE1),
        Config.Test.User2.matrix_id: create_db_if_not_exists(Config.DB_FILE2),
    } if Config.is_test else { 'default': create_db_if_not_exists(Config.DB_FILE1)}
    def session():
        if Config.is_test:
            return DB.sessions[Context.matrix_user_id()]
        else:
            return list(DB.sessions.values())[0]
