import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models.models import (
    user_secret_signature_share,
    wallet_key_generation_share,
)
from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.transaction_response_dto import TransactionResponseDTO
import json
import Config
import uuid
import sqlalchemy

from Services.Context import Context

Base = declarative_base()


class User(Base):
    __tablename__ = "User"
    email = Column(String, primary_key=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    homeserver_url = Column(String, nullable=True)
    matrix_user_id = Column(String, nullable=True)

class Friend(Base):
    __tablename__ = "Friend"
    email = Column(String, primary_key=True, nullable=False)
    matrix_id = Column(String, primary_key=False, nullable=False)


class Wallet(Base):
    __tablename__ = "Wallet"
    wallet_id = Column(
        String, primary_key=True, nullable=False
    )  # This will be the room Id.
    threshold = Column(Integer, nullable=False)
    name = Column(String, nullable=True)
    max_num_of_users = Column(Integer, nullable=False)
    users = Column(
        Text, nullable=True
    )  # @alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    configuration = Column(Text, nullable=True)  # User secret (real type is user_secret_signature_share)
    curve_name = Column(Text, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")
    users_data = relationship("WalletUserData", back_populates="wallet")
    signature_shares = relationship(
        "WalletSignatureSharesData", back_populates="wallet"
    )

    def set_room_secret_user_data(self, data: user_secret_signature_share):
        self.configuration = data.model_dump_json()

    def get_room_secret_user_data(self):
        if self.configuration:
            data = json.loads(self.configuration)
            return user_secret_signature_share.model_validate(data)
        return None


class Transaction(Base):
    __tablename__ = "Transaction"
    transaction_id = Column(String, primary_key=True, nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Integer, nullable=True)
    shrunken_secret_share = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    wallet_id = Column(String, ForeignKey("Wallet.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")
    
    @classmethod
    def from_dto(cls, transaction_dto: "TransactionDTO"):
        return cls(
            transaction_id=transaction_dto.id,
            details=transaction_dto.details,
            wallet_id=transaction_dto.wallet_id,
            status=transaction_dto.status.value,
            shrunken_secret_share=transaction_dto.shrunken_secret_share,
            amount=transaction_dto.amount,
            name=transaction_dto.name
        )

class TransactionUserData(Base):
    """
    Stores user-specific data for MtA and MtAwc protocols within a transaction.
    Contains only the final computed integer results.
    """
    __tablename__ = "TransactionUserData"
    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    user_matrix_id = Column(String, primary_key=True, nullable=False)
    user_index = Column(Integer, primary_key=True, nullable=False)

    # MtA & MtAwc result values (final integer shares)
    mta_user_as_alice_value = Column(Integer, nullable=True)  # Stores Alice's final α
    mta_user_as_bob_value = Column(Integer, nullable=True)  # Stores Bob's final β
    mta_wc_as_alice_value = Column(Integer, nullable=True)  # Stores Alice's final MtAwc share
    mta_wc_user_as_bob_value = Column(Integer, nullable=True)  # Stores Bob's final MtAwc share

    def add_mta_result(self, result_value: int, role: str, protocol_type: str):
        """
        Stores the final MtA or MtAwc integer result for the user based on their role.

        :param result_value: Final computed integer result from MtA or MtAwc.
        :param role: 'alice' or 'bob' (denoting user role in MtA/MtAwc)
        :param protocol_type: 'mta' or 'mta_wc' (denoting MtA or MtAwc protocol)
        """
        if protocol_type == "mta":
            if role == "alice":
                self.mta_user_as_alice_value = result_value
            elif role == "bob":
                self.mta_user_as_bob_value = result_value
        elif protocol_type == "mta_wc":
            if role == "alice":
                self.mta_wc_as_alice_value = result_value
            elif role == "bob":
                self.mta_wc_user_as_bob_value = result_value

    def get_mta_result(self, role: str, protocol_type: str) -> int:
        """
        Retrieves the stored MtA or MtAwc final integer result for the user.

        :param role: 'alice' or 'bob' (denoting user role in MtA/MtAwc)
        :param protocol_type: 'mta' or 'mta_wc' (denoting MtA or MtAwc protocol)
        :return: Final integer result (or None if not found).
        """
        if protocol_type == "mta":
            return self.mta_user_as_alice_value if role == "alice" else self.mta_user_as_bob_value
        elif protocol_type == "mta_wc":
            return self.mta_wc_as_alice_value if role == "alice" else self.mta_wc_user_as_bob_value

    def remove_mta_result(self, role: str, protocol_type: str):
        """
        Resets the stored MtA or MtAwc final result for the user.

        :param role: 'alice' or 'bob' (denoting user role in MtA/MtAwc)
        :param protocol_type: 'mta' or 'mta_wc' (denoting MtA or MtAwc protocol)
        """
        if protocol_type == "mta":
            if role == "alice":
                self.mta_user_as_alice_value = None
            elif role == "bob":
                self.mta_user_as_bob_value = None
        elif protocol_type == "mta_wc":
            if role == "alice":
                self.mta_wc_as_alice_value = None
            elif role == "bob":
                self.mta_wc_user_as_bob_value = None


    @classmethod
    def from_dto(cls, transaction_dto: "TransactionDTO"):
        # Create a new instance and populate it with the DTO values
        transaction = cls(
            transaction_id=transaction_dto.id,
            details=transaction_dto.details,
            wallet_id=transaction_dto.wallet_id,
            status=transaction_dto.status.value,
        )
        return transaction


class WalletUserData(Base):
    """
    One per user X Wallet
    """

    __tablename__ = "WalletUserData"
    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_index = Column(Integer, nullable=False)
    user_matrix_id = Column(String, nullable=False)
    user_public_keys_data = Column(JSON, nullable=False, default={})  # Paillier Public key and Modulus data - that is the user_public_share
    g_power_x = Column(Integer, nullable=True)
    wallet_id = Column(String, ForeignKey("Wallet.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="users_data")

    __table_args__ = (
        sqlalchemy.UniqueConstraint('user_matrix_id', 'wallet_id', name='unique_user_wallet'),
    )


class WalletSignatureSharesData(Base):
    __tablename__ = "WalletSignatureSharesData"
    share_id = Column(String, primary_key=True, nullable=False)
    share_index = Column(Integer, primary_key=False, nullable=False)
    user_matrix_id = Column(String,primary_key=False, nullable=True)
    share_data = Column(
        JSON, nullable=False, default={}
    )  # data of to dict/from_dict of key_generation_share.
    wallet_id = Column(String, ForeignKey("Wallet.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="signature_shares")
    
    def get_signature_share(self, user_index: int) -> wallet_key_generation_share:
        """
        this is not is use - need to check if works
        """
        return wallet_key_generation_share.from_dict(self)

class TransactionResponse(Base):
    __tablename__ = "TransactionResponse"
    id = Column(Integer, primary_key=True, nullable=False)
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    stage = Column(Integer, nullable=False)
    response = Column(Boolean, nullable=False)
    
    @classmethod
    def from_dto(cls, transaction_response_dto: TransactionResponseDTO):
        return cls(
            transaction_id=transaction_response_dto.transaction_id,
            stage=transaction_response_dto.stage,
            response=transaction_response_dto.response
        )
    
class Mta_As_Alice_Users_Data(Base):
    """
    Stores data for the MtA protocol where the current user played as Alice.
    """

    __tablename__ = "Mta_As_Alice_Users_Data"

    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    user_index = Column(Integer, nullable=False)  # Index of Alice in the transaction
    counterparty_index = Column(Integer, nullable=False)  # Index of Bob in the transaction

    a = Column(Integer, nullable=True)  # Alice's secret integer value
    enc_a = Column(JSON, nullable=True)  # EncryptedNumber (serialized as JSON)
    commitment_of_a = Column(JSON, nullable=True)  # AliceZKProof_Commitment (JSON format)
    
    bobs_challenge = Column(Integer, nullable=True)  # Integer challenge from Bob
    bobs_encrypted_value = Column(JSON, nullable=True)  # EncryptedNumber (JSON format)
    bobs_commitment = Column(JSON, nullable=True)  # Bob_ZKProof_ProverCommitment (JSON format)

    alice_challenge = Column(Integer, nullable=True)  # Integer challenge from Alice to Bob
    bob_proof_for_challenge = Column(JSON, nullable=True)  # Bob_ZKProof_Proof_For_Challenge (JSON format)

    transaction = relationship("Transaction", back_populates="mta_as_alice_data")

class Mta_As_Bob_Users_Data(Base):
    """
    Stores data for the MtA protocol where the current user played as Bob.
    """

    __tablename__ = "Mta_As_Bob_Users_Data"
    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    user_index = Column(Integer, nullable=False)  # Bob's index
    counterparty_index = Column(Integer, nullable=False)  # Alice's index
    b = Column(Integer, nullable=True)  # Bob's secret integer value
    enc_a = Column(JSON, nullable=True)  # Alice’s encrypted value (EncryptedNumber, serialized as JSON)
    commitment_of_a = Column(JSON, nullable=True)  # Alice’s commitment (AliceZKProof_Commitment, serialized as JSON)
    bobs_challenge = Column(Integer, nullable=True)  # Integer challenge sent to Alice
    enc_result = Column(JSON, nullable=True)  # Encrypted (ab + β') (EncryptedNumber, serialized as JSON)
    bobs_commitment = Column(JSON, nullable=True)  # Bob’s commitment (Bob_ZKProof_ProverCommitment, serialized as JSON)
    beta_prime = Column(Integer, nullable=True)  # Bob’s additive term for decryption
    alice_challenge = Column(Integer, nullable=True)  # Challenge received from Alice
    bob_proof_for_challenge = Column(JSON, nullable=True)  # Bob’s proof for Alice’s challenge (Bob_ZKProof_Proof_For_Challenge, serialized as JSON)

class MtaWc_As_Alice_Users_Data(Base):
    """
    Stores data for the MtaWc protocol where the current user played as Alice.
    """

    __tablename__ = "MtaWc_As_Alice_Users_Data"

    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    user_index = Column(Integer, nullable=False)  # Index of Alice in the transaction
    counterparty_index = Column(Integer, nullable=False)  # Index of Bob in the transaction
    a = Column(Integer, nullable=True)  # Alice's secret integer value
    enc_a = Column(JSON, nullable=True)  # EncryptedNumber (serialized as JSON)
    commitment_of_a = Column(JSON, nullable=True)  # AliceZKProof_Commitment (JSON format)
    bobs_challenge = Column(Integer, nullable=True)  # Integer challenge from Bob
    bobs_encrypted_value = Column(JSON, nullable=True)  # EncryptedNumber (JSON format)
    bobs_commitment = Column(JSON, nullable=True)  # Bob_ZKProof_ProverCommitment (JSON format)
    alice_challenge = Column(Integer, nullable=True)  # Integer challenge from Alice to Bob
    bob_proof_for_challenge = Column(JSON, nullable=True)  # Bob_ZKProof_Proof_For_Challenge (JSON format)
    transaction = relationship("Transaction", backref="mtawc_as_alice_data")


class MtaWc_As_Bob_Users_Data(Base):
    """
    Stores data for the MtaWc protocol where the current user played as Bob.
    """

    __tablename__ = "MtaWc_As_Bob_Users_Data"
    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("Transaction.transaction_id"), nullable=False)
    user_index = Column(Integer, nullable=False)  # Bob's index
    counterparty_index = Column(Integer, nullable=False)  # Alice's index
    b = Column(Integer, nullable=True)  # Bob's secret integer value
    enc_a = Column(JSON, nullable=True)  # Alice's encrypted value (EncryptedNumber, serialized as JSON)
    commitment_of_a = Column(JSON, nullable=True)  # Alice's commitment (AliceZKProof_Commitment, serialized as JSON)
    bobs_challenge = Column(Integer, nullable=True)  # Integer challenge sent to Alice
    enc_result = Column(JSON, nullable=True)  # Encrypted (ab + β') (EncryptedNumber, serialized as JSON)
    bobs_commitment = Column(JSON, nullable=True)  # Bob's commitment (Bob_ZKProof_ProverCommitment, serialized as JSON)
    beta_prime = Column(Integer, nullable=True)  # Bob's additive term for decryption
    alice_challenge = Column(Integer, nullable=True)  # Challenge received from Alice
    bob_proof_for_challenge = Column(JSON, nullable=True)  # Bob's proof for Alice's challenge (Bob_ZKProof_Proof_For_Challenge, serialized as JSON)



def create_db_if_not_exists(db_file_name): 
    current_path = os.path.dirname(
            os.path.abspath(__file__)
        )
    abs_path = os.path.join(current_path, db_file_name)
    
    if os.path.exists(abs_path) and Config.is_test:
        os.remove(abs_path)
    
    engine = create_engine(f"sqlite:///{abs_path}")
    if not os.path.exists(abs_path):    
        Base.metadata.create_all(engine)
    # Session maker
    Session = sessionmaker(bind=engine)
    return Session


class DB():
    sessions = {
        Config.Test.User1.matrix_id: create_db_if_not_exists(Config.DB_FILE1),
        Config.Test.User2.matrix_id: create_db_if_not_exists(Config.DB_FILE2),
    } if Config.is_test else { 'default': create_db_if_not_exists(Config.DB_FILE1)}
    def session():
        if Config.is_test:
            return DB.sessions[Context.matrix_user_id()]()
        else:
            return list(DB.sessions.values())[0]()
