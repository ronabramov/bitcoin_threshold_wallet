import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models.models import user_public_share, user_secret_signature_share, user_key_generation_share
from models.DTOs.transaction_dto import TransactionDTO
import json


Base = declarative_base()
DB_FILE = "/local_db/local_db.sqlite"

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
    wallet_id = Column(String, primary_key=True, nullable=False) #This will be the room Id.
    threshold = Column(Integer, nullable=False)
    max_num_of_users = Column(Integer, nullable=False)
    users = Column(Text, nullable=True) #@alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    configuration = Column(Text, nullable=True) # User secret
    curve_name = Column(Text, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")
    users_data = relationship("Room_User_Data", back_populates="wallet")
    signature_shares = relationship("Room_Signature_Shares_Data", back_populates="wallet")

    #We should save here also the participants data from the Room_Users_Data and destroy Room_Users_Data object. 
    # This should happen in way s.t every other user will have row in another table with the room_id and the user as ids and the json of his data.
    #When inserting wallet we insert these rows afterwards, and when pulling a wallet we pull also that data.

    def set_room_secret_user_data(self, data : user_secret_signature_share):
        self.configuration = data.model_dump_json()

    def get_room_secret_user_data(self):
        if self.configuration:
            data = json.loads(self.configuration)
            return user_secret_signature_share.model_validate_json(data)
        return None
    


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, nullable=False)
    details = Column(Text, nullable=True)
    approvers = Column(Text, nullable=True)
    approvals_counter = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")

    @classmethod
    def from_dto(cls, transaction_dto: "TransactionDTO"):
        # Create a new instance and populate it with the DTO values
        transaction = cls(
            transaction_id=transaction_dto.id,
            details=transaction_dto.details,
            approvers=transaction_dto.approvers,
            approvals_counter=transaction_dto.approvers_counter,
            wallet_id=transaction_dto.wallet_id,
            status=transaction_dto.stage.value 
        )
        return transaction    

class Room_User_Data(Base):
    """
    One per room - include all necessary participants' keys.
    """
    __tablename__ = "room_user_data"
    
    user_index = Column(Integer, primary_key=True, nullable=False)
    user_matrix_id = Column(String, primary_key=True, nullable=False)
    user_public_keys_data = Column(JSON, nullable=False, default={})  #Paillier Public key and Modulus data
    signature_shared_data = Column(JSON, nullable=False, default={})  # Includes the signature share the user sent in channel
    mta_data = Column(JSON, nullable=False, default={})  # Stores relevant data for MTA process with the user

    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="room_user_data")

    ### PARTICIPANT DATA MANAGEMENT ###
    
    def set_user_public_keys(self, user_data: user_public_share):
        self.user_public_keys_data = user_data.to_dict()

    def get_user_public_keys(self) -> user_public_share:
        return user_public_share.from_dict(self.user_public_keys_data) if self.user_public_keys_data else None

    def update_user_public_keys(self, user_data: user_public_share):
        if not self.user_public_keys_data:
            raise ValueError(f"No user public key data found for user {self.user_matrix_id}")

        self.user_public_keys_data = user_data.to_dict()

    def remove_user_public_keys(self):
        self.user_public_keys_data = {}

    ### SIGNATURE SHARE MANAGEMENT ###
    
    def add_signature_share(self, signature_share: dict):
        self.signature_shared_data = signature_share

    def get_signature_share(self) -> dict:
        return self.signature_shared_data

    def remove_signature_share(self):
        self.signature_shared_data = {}

    ### MTA DATA MANAGEMENT ###
    
    def add_mta_data(self, mta_info: dict):
        self.mta_data = mta_info

    def get_mta_data(self) -> dict:
        return self.mta_data

    def remove_mta_data(self):
        self.mta_data = {}

class Room_Signature_Shares_Data(Base):
    share_index = Column(Integer, primary_key=True, nullable=False)
    share_data = Column(JSON, nullable=False, default={}) # data of to dict/from_dict of user_key_generation_share.
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")

    def get_signature_share(self, user_index : int) -> user_key_generation_share:
        return user_key_generation_share.from_dict(self.share_data)


# check if the database exists
if not os.path.exists(DB_FILE):
    # Create SQLite engine
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base.metadata.create_all(engine)
else:
    engine = create_engine(f"sqlite:///{DB_FILE}")

# Session maker
Session = sessionmaker(bind=engine)

# this is the session that will be used to interact with the database
session = Session()
