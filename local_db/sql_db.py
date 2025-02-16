import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models.models import user_public_share, room_secret_user_data
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

    #We should save here also the participants data from the Room_Users_Data and destroy Room_Users_Data object. 
    # This should happen in way s.t every other user will have row in another table with the room_id and the user as ids and the json of his data.
    #When inserting wallet we insert these rows afterwards, and when pulling a wallet we pull also that data.

    def set_room_secret_user_data(self, data : room_secret_user_data):
        self.configuration = data.model_dump_json()

    def get_room_secret_user_data(self):
        if self.configuration:
            data = json.loads(self.configuration)
            return room_secret_user_data.model_validate_json(data)
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
        """ 
        Stores the `user_public_share` object in `user_public_keys_data`. 
        This replaces the previous data.
        """
        self.user_public_keys_data = user_data.to_dict()

    def get_user_public_keys(self) -> user_public_share:
        """ 
        Retrieves the user's `user_public_share` data as an object. 
        Returns a `user_public_share` instance.
        """
        return user_public_share.from_dict(self.user_public_keys_data) if self.user_public_keys_data else None

    def update_user_public_keys(self, user_data: user_public_share):
        """ 
        Updates the stored `user_public_share` object while preserving existing fields.
        Raises an error if no data exists.
        """
        if not self.user_public_keys_data:
            raise ValueError(f"No user public key data found for user {self.user_matrix_id}")

        self.user_public_keys_data = user_data.to_dict()

    def remove_user_public_keys(self):
        """ 
        Clears the stored `user_public_share` object.
        This action effectively removes all stored public keys for the user.
        """
        self.user_public_keys_data = {}

    ### SIGNATURE SHARE MANAGEMENT ###
    
    def add_signature_share(self, signature_share: dict):
        """ 
        Stores the user's signature share data.
        This is used in the signing protocol.
        """
        self.signature_shared_data = signature_share

    def get_signature_share(self) -> dict:
        """ 
        Retrieves the signature share of the user. 
        Returns an empty dictionary if no share is found.
        """
        return self.signature_shared_data

    def remove_signature_share(self):
        """ 
        Removes the stored signature share data for the user.
        This will clear all signature share information.
        """
        self.signature_shared_data = {}

    ### MTA DATA MANAGEMENT ###
    
    def add_mta_data(self, mta_info: dict):
        """ 
        Adds or updates MTA-related data for this user. 
        This information is used during the multi-party computation process.
        """
        self.mta_data = mta_info

    def get_mta_data(self) -> dict:
        """ 
        Retrieves the MTA-related data of the user. 
        Returns an empty dictionary if no data exists.
        """
        return self.mta_data

    def remove_mta_data(self):
        """ 
        Removes the stored MTA-related data for this user. 
        This clears all multi-party computation information.
        """
        self.mta_data = {}



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
