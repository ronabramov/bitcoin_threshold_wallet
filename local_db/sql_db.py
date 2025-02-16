import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models.models import room_public_user_data, room_secret_user_data
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
    users = Column(Text, nullable=True) #@alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    configuration = Column(Text, nullable=True)#What configurations?
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
    One per transaction- include all necessary particpants' keys.
    """
    __tablename__ = "room_user_data"
    user_index = Column(Integer, primary_key=True, nullable=False)
    user_matrix_id = Column(String, primary_key=True, nullable=False)
    user_public_keys_data = Column(JSON, nullable=False, default={}) #Paillier Public key and Modulus data
    signature_shared_data = Column(JSON, nullable=False, default={}) # Include the signature share the user sent in channel
    mta_data = Column(JSON, nullable=False, default={}) #will store relevant data for mta process with the user
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="room_user_data")
    
    def add_participant(self, user_data: room_public_user_data):
        """ Adds a new participant using a `room_public_user_data` object. """
        index = str(user_data.user_index)
        if index in self.user_public_keys_data:
            raise ValueError(f"Participant with index {user_data.user_index} already exists.")

        self.user_public_keys_data[index] = user_data.to_dict()

    def get_participant(self, index: int) -> room_public_user_data:
        """ Retrieves participant data as a `room_public_user_data` object. """
        data = self.user_public_keys_data.get(str(index))
        return room_public_user_data.from_dict(data) if data else None

    def update_participant(self, user_data: room_public_user_data):
        """ Updates participant data while preserving existing fields. """
        index = str(user_data.user_index)
        if index not in self.user_public_keys_data:
            raise ValueError(f"Participant with index {user_data.user_index} not found.")

        self.user_public_keys_data[index] = user_data.to_dict()

    def remove_participant(self, index: int):
        """ Removes a participant from the transaction room. """
        if str(index) in self.user_public_keys_data:
            del self.user_public_keys_data[str(index)]
        else:
            raise ValueError(f"Participant with index {index} not found.")

    def list_participants(self):
        """ Returns all participants as `room_public_user_data` objects. """
        return {int(k): room_public_user_data.from_dict(v) for k, v in self.user_public_keys_data.items()}
    
        ### SIGNATURE SHARE MANAGEMENT ###
    
    def add_signature_share(self, user_index: int, signature_share: dict):
        """ Stores the user's signature share data. """
        self.signature_shared_data[str(user_index)] = signature_share

    def get_signature_share(self, user_index: int) -> dict:
        """ Retrieves the signature share of a specific user. """
        return self.signature_shared_data.get(str(user_index), {})

    def remove_signature_share(self, user_index: int):
        """ Removes signature share data for a participant. """
        if str(user_index) in self.signature_shared_data:
            del self.signature_shared_data[str(user_index)]

        ### MTA DATA MANAGEMENT ###

    def add_mta_data(self, participant_index: int, mta_info: dict):
        """ Adds or updates MTA-related data for a specific participant. """
        self.mta_data[str(participant_index)] = mta_info

    def get_mta_data(self, participant_index: int) -> dict:
        """ Retrieves MTA-related data for a participant. """
        return self.mta_data.get(str(participant_index), {})

    def remove_mta_data(self, participant_index: int):
        """ Removes MTA-related data for a participant. """
        if str(participant_index) in self.mta_data:
            del self.mta_data[str(participant_index)]



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
