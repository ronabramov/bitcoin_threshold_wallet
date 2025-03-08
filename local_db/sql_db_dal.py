from local_db import sql_db
from local_db.sql_db import DB, Transaction, Mta_As_Alice_Users_Data, Mta_As_Bob_Users_Data
from typing import List
from models.DTOs.transaction_dto import TransactionDTO as TransactionDTO
from models.transaction_status import TransactionStatus
from models.models import  user_public_share, wallet_key_generation_share, GPowerX
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from phe import EncryptedNumber, PaillierPublicKey
from common_utils import serialize_encryped_number, deserialize_encrypted_number
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_Proof_For_Challenge, Bob_ZKProof_ProverCommitment, Bob_ZKProof_RegMta_Prover_Settings, Bob_ZKProof_RegMta_Settings
from Services.Context import Context

def get_friend_by_email(email : str) -> sql_db.Friend:
    with DB.session() as session:
        try:
            friend = session.query(sql_db.Friend).filter(sql_db.Friend.email == email).first()
            if not friend :
                print (f"Couldn't find friend with email {email}")
                raise FileNotFoundError(f"Friend with email {email} couldn't be found")
            return friend
        except Exception as e:
            print(f"There was and error while trying to retrieve friend with email :  {email}", e)

def get_friend_by_matrix_id(matrix_id : str) -> sql_db.Friend:
    with DB.session() as session:
        friend = session.query(sql_db.Friend).filter(sql_db.Friend.matrix_id == matrix_id).first()
        return friend

def get_all_user_friends() -> List[sql_db.User]:
    with DB.session() as session:
        users = session.query(sql_db.Friend).all()
        return users

def get_wallet_by_id(wallet_id : str) -> sql_db.Wallet:
    with DB.session() as session:
        try:
            wallet = session.query(sql_db.Wallet).filter(sql_db.Wallet.wallet_id == wallet_id).first()
            if not wallet :
                print (f"Wallet with Id : {wallet_id} couldn't be found")
                raise FileNotFoundError(f"wallet with Id : {wallet_id} couldn't be found")
            return wallet
        except Exception as e:
            print(f"There was and error while trying to retrieve wallet {wallet_id}", e)

def get_my_wallets() -> List[sql_db.Wallet]:
    with DB.session() as session:
        wallets = session.query(sql_db.Wallet).all()
        return wallets

def get_transaction_by_id(transaction_id : str) -> sql_db.Transaction:
    with DB.session() as session:
        try:
            transaction = session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
            if not transaction :
                print (f"Couldn't find transaction with id : {transaction_id}")
                return None
            return transaction
        except Exception as e:
            print(f"There was and error while trying to retrieve transaction {transaction_id}", e)

def get_transactions_by_wallet_id(wallet_id : str, should_convert_to_dto = False):
    with DB.session() as session:
        try:
            transactions = session.query(sql_db.Transaction).filter(sql_db.Transaction.wallet_id == wallet_id).all()
            if not transactions :
                print (f"Couldn't find transaction for wallet  : {wallet_id}")
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
    with DB.session() as session:
        shares = session.query(sql_db.WalletSignatureSharesData).filter_by(wallet_id=wallet_id).all()
        return [wallet_key_generation_share.from_dict(share) for share in shares]


def insert_signature_share(wallet_id: str, share_data: wallet_key_generation_share) -> bool:
    share_index = share_data.target_user_index
    with DB.session() as session:
        try:
            share_entry = sql_db.WalletSignatureSharesData(
                share_id = f'{wallet_id}_{share_index}',
                share_index=share_index,
                share_data=share_data.to_dict(),
                wallet_id=wallet_id
            )
            session.add(share_entry)
            session.commit()
            print(f"Successfully inserted signature share {share_index} for wallet {wallet_id}.")
            return True
    
        except Exception as e:
            session.rollback()
            print(f"Failed to insert signature share {share_index} for wallet {wallet_id}: {e}")
            return False


def insert_multiple_signature_shares(wallet_id: str, shares: list[wallet_key_generation_share]) -> bool:
    success = True
    for share in shares:
        result = insert_signature_share(wallet_id, share_data=share)
        if not result:
            success = False
    return success


def insert_new_transaction(transaction : TransactionDTO) -> bool:
    with DB.session() as session:
        try:
            transaction_to_insert = sql_db.Transaction.from_dto(transaction_dto=transaction)
            session.add(transaction_to_insert)
            session.commit()
            print(f"Successfully inserted transaction {transaction.id}")
            return True
        except Exception as e:
            print(f'failed to insert transaction {transaction.id} to db.', e)
            return False

def update_transaction(transaction : Transaction) -> bool:
    with DB.session() as session:
        try:
            session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction.id).update(transaction)
            session.commit()
            print(f"Successfully updated transaction {transaction.id}")
            return True
        except Exception as e:
            print(f'failed to update transaction {transaction.id} to db.', e)
            return False

def insert_new_wallet(wallet : sql_db.Wallet) -> bool:
    with DB.session() as session:
        try:
            session.add(wallet)
            session.commit()
            print(f"Successfully inserted wallet {wallet.wallet_id} to db")
            return True
        except Exception as e:
            print(f"Failed to insert wallet {wallet.wallet_id}", e)
            return False

def insert_my_wallet_user_data(wallet_id : str,  user_public_keys : user_public_share):
    insert_new_wallet_user_data(wallet_id=wallet_id, user_index=user_public_keys.user_index, user_matrix_id=Context.matrix_user_id(), user_public_share=user_public_keys)

def get_my_wallet_user_data(wallet_id : str) -> sql_db.WalletUserData:
    with DB.session() as session:
        return session.query(sql_db.WalletUserData).filter(sql_db.WalletUserData.wallet_id == wallet_id, sql_db.WalletUserData.user_matrix_id == Context.matrix_user_id()).first()

def get_all_wallet_user_data(wallet_id : str) -> List[sql_db.WalletUserData]:
    with DB.session() as session:
        return session.query(sql_db.WalletUserData).filter(sql_db.WalletUserData.wallet_id == wallet_id).all()

def get_specific_wallet_user_data(wallet_id : str, traget_user_index_in_wallet : int)-> sql_db.WalletUserData:
    with DB.session() as session:
        return session.query(sql_db.WalletUserData).filter(sql_db.WalletUserData.wallet_id == wallet_id, sql_db.WalletUserData.user_index == traget_user_index_in_wallet).first()

# TODO: maybe remove matrix id and index as parameters since we get them from the user_public_keys
def insert_new_wallet_user_data(wallet_id : str, user_index : int, user_matrix_id : str, user_public_share : user_public_share):
    with DB.session() as session:
        try:
            #  check if the user share already exists in the db
            user_share = session.query(sql_db.WalletUserData).filter(sql_db.WalletUserData.user_matrix_id == user_matrix_id, sql_db.WalletUserData.wallet_id == wallet_id).first()
            if user_share:
                print(f"User share for user {user_matrix_id} already exists in the db")
                return True
            room_user_data = sql_db.WalletUserData(user_index = user_index, user_matrix_id=user_matrix_id,
                                                    user_public_keys_data = user_public_share.to_dict(), wallet_id=wallet_id)
            session.add(room_user_data)
            session.commit()
            print(f"Successfully inserted room's user data for user {user_matrix_id} in wallet {wallet_id} to db")
            return True
        except Exception as e:
            print(f"Failed to insert user {user_matrix_id} into wallet {wallet_id}", e)
            return False

def insert_new_friend(user_email : str, user_matrix_id : str) -> bool:
    with DB.session() as session:
        friend = session.query(sql_db.Friend).filter(sql_db.Friend.matrix_id == user_matrix_id).first()
        if friend is not None:
            print(f"Friend {user_matrix_id} already exists")
            return True
        try:
            friend_db_object = sql_db.Friend(email=user_email, matrix_id = user_matrix_id)
            session.add(friend_db_object)
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to inserting user {user_matrix_id} into Friends table", e)
            session.rollback()
            return False

def remove_friend(email : str) -> bool:
    with DB.session() as session:
        try:
            friend = session.query(sql_db.Friend).filter(sql_db.Friend.email == email).first()
            if not friend:
                print(f"Friend {email} not found")
                return True
            session.delete(friend)
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to remove friend {email}", e)
            session.rollback()
            return False
            
def map_transaction_to_dto(transaction : sql_db.Transaction) -> TransactionDTO:
    transaction_dto = transaction_dto = TransactionDTO(
    id=transaction.transaction_id,  
    name="", 
    details=transaction.details, 
    wallet_id=transaction.wallet_id
    )
    transaction_dto.status = TransactionStatus[transaction.status]
    return transaction_dto

def update_signature_share(wallet_id : str, share : wallet_key_generation_share) -> bool:
    with DB.session() as session:
        try:
            share_db_object = session.query(sql_db.WalletSignatureSharesData).filter(
                sql_db.WalletSignatureSharesData.share_index == share.target_user_index, 
                sql_db.WalletSignatureSharesData.wallet_id == wallet_id).first()
            share_db_object.user_matrix_id = share.target_user_matrix_id
            share_db_object.share_data = share.to_dict()
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to update signature share for wallet {wallet_id}", e)

        
def get_transaction_responses_by_transaction_id(transaction_id : str) -> sql_db.TransactionResponse:
    with DB.session() as session:
        try:    
            return session.query(sql_db.TransactionResponse).filter(sql_db.TransactionResponse.transaction_id == transaction_id).all()
        except Exception as e:
            print(f"Failed to get transaction response for transaction {transaction_id}", e)
            return None

def insert_transaction_response(transaction_response : TransactionResponseDTO) -> bool:
    with DB.session() as session:
        try:
            transaction_response_to_insert = sql_db.TransactionResponse.from_dto(transaction_response_dto=transaction_response)
            session.add(transaction_response_to_insert)
            session.commit()
            print(f"Successfully inserted transaction response {transaction_response.transaction_id}")
            return True
        except Exception as e:
            print(f"Failed to insert transaction response {transaction_response.transaction_id}", e)
            return False
    
def insert_transaction_secret(transaction_id : str, shrunken_secret_share : int) -> bool:
    with DB.session() as session:
        try:
            transaction = session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
            if not transaction:
                print(f"Transaction {transaction_id} not found")
                return False
            transaction.shrunken_secret_share = shrunken_secret_share
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to insert transaction secret {transaction_id}", e)
            session.rollback()
            return False

def get_transaction_secret(transaction_id : str):
    """
    Do not broadcast!
    """
    with DB.session() as session:
        try:
            transaction = session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
            return transaction.shrunken_secret_share
        except Exception as e:
            print(f"Failed to get transaction secret {transaction_id}", e)
            return None

def insert_transaction_user_data(transaction_id : str, user_index : int, user_matrix_id : str) -> bool:
    with DB.session() as session:
        try:
            transaction_user_data = sql_db.TransactionUserData(transaction_id=transaction_id, user_index=user_index, user_matrix_id=user_matrix_id)
            session.add(transaction_user_data)
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to insert transaction user data {transaction_id}", e)
            return False

def update_transaction_user_data(transaction_user_data: sql_db.TransactionUserData) -> bool:
    with DB.session() as session:
        try:
            session.query(sql_db.TransactionUserData).filter(
                sql_db.TransactionUserData.transaction_id == transaction_user_data.transaction_id,
                sql_db.TransactionUserData.user_index == transaction_user_data.user_index
            ).delete()

            session.add(transaction_user_data)

            session.commit()
            print(f"Successfully replaced TransactionUserData for transaction {transaction_user_data.transaction_id} and user {transaction_user_data.user_index}.")
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update TransactionUserData for transaction {transaction_user_data.transaction_id} and user {transaction_user_data.user_index}: {e}")
            return False

def get_transaction_user_data_by_index(transaction_id : str, user_index : int) -> sql_db.TransactionUserData:
    with DB.session() as session:
        return session.query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id, sql_db.TransactionUserData.user_index == user_index).first()

def get_transaction_user_data_by_matrix_id(transaction_id : str, user_matrix_id : str) -> sql_db.TransactionUserData:
    with DB.session() as session:
        return session.query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id, sql_db.TransactionUserData.user_matrix_id == user_matrix_id).first()


def get_all_transaction_user_data(transaction_id : str) -> List[sql_db.TransactionUserData]:
    with DB.session() as session:
        return session.query(sql_db.TransactionUserData).filter(sql_db.TransactionUserData.transaction_id == transaction_id).all()
    
def insert_g_power_x(g_power_x : GPowerX):
    with DB.session() as session:
        try:
            user_data = session.query(sql_db.WalletUserData).filter(sql_db.WalletUserData.user_matrix_id == g_power_x.user_matrix_id, sql_db.WalletUserData.wallet_id == g_power_x.wallet_id).first()
            if not user_data:
                print(f"User data for user {g_power_x.user_matrix_id} in wallet {g_power_x.wallet_id} not found")
                return False
            user_data.g_power_x = g_power_x.value
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to insert g_power_x {g_power_x}", e)
            return False
        
        
def get_user_by_email(email : str) -> sql_db.User:
    with DB.session() as session:
        return session.query(sql_db.User).filter(sql_db.User.email == email).first()


def add_user(email : str, hashed_password : str, matrix_user_id : str) -> bool:
    with DB.session() as session:
        user = sql_db.User(email=email, hashed_password=hashed_password, matrix_user_id=matrix_user_id)
        session.add(user)
        session.commit()
        return True


def delete_wallet(wallet_id : str) -> bool:
    with DB.session() as session:
        session.query(sql_db.Wallet).filter(sql_db.Wallet.wallet_id == wallet_id).delete()
        session.commit()
        return True
    
# ================================================================================================
# MTA Protocl Methods - When the user is in Alice's shoes. The relevant steps are:
# 1. Store Alices' a and enc_a
# 2. Store Alice's Commitment
# 3. Store Bob's Challenge
# 4. Store Bob's Encrypted Response & Bob's Commitment
# 5. Store Alice's Challenge
# 6. Store Bob's Proof for Alice's challenge (mainly for tracking...)
# ================================================================================================

#RON TODO: handle the encrypted_number to dict


def get_mta_as_alice_user_data(transaction_id: str, user_index: int, user_paillier_pub_key : PaillierPublicKey,
                                counterparty_index: int, counter_party_paillier_pub_key : PaillierPublicKey) -> Mta_As_Alice_Users_Data:
    """
    Retrieves MtA data where the user played as Alice for a specific counterparty.
    Converts JSON fields back into models safely, ensuring missing fields don't cause exceptions.
    """
    with DB.session() as session:
        record = session.query(Mta_As_Alice_Users_Data).filter(
            Mta_As_Alice_Users_Data.transaction_id == transaction_id,
            Mta_As_Alice_Users_Data.user_index == user_index,  # Alice's index
            Mta_As_Alice_Users_Data.counterparty_index == counterparty_index  # Bob's index
        ).first()

        if not record:
            return None

        # Convert JSON fields back into models only if they exist
        record.enc_a = deserialize_encrypted_number(record.enc_a, user_paillier_pub_key) if record.enc_a else None
        record.commitment_of_a = AliceZKProof_Commitment.from_dict(record.commitment_of_a) if record.commitment_of_a else None
        record.bobs_encrypted_value = deserialize_encrypted_number(record.bobs_encrypted_value, counter_party_paillier_pub_key) if record.bobs_encrypted_value else None
        record.bobs_commitment = Bob_ZKProof_ProverCommitment.from_dict(record.bobs_commitment) if record.bobs_commitment else None
        record.bob_proof_for_challenge = Bob_ZKProof_Proof_For_Challenge.from_dict(record.bob_proof_for_challenge) if record.bob_proof_for_challenge else None

        return record

def insert_alice_a_and_enc_a(transaction_id: str, user_index: int, counterparty_index: int,
                             a: int, enc_a: EncryptedNumber) -> bool:
    with DB.session() as session:
        try:
            entry = Mta_As_Alice_Users_Data(transaction_id=transaction_id, user_index=user_index, counterparty_index=counterparty_index,
                a=a, enc_a=serialize_encryped_number(encrypted_number=enc_a))
            session.add(entry)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to insert Alice's secret for transaction {transaction_id}: {e}")
            return False
        
def update_alice_commitment(transaction_id: str, user_index: int, commitment_of_a: AliceZKProof_Commitment) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Alice_Users_Data).filter(
                Mta_As_Alice_Users_Data.transaction_id == transaction_id,
                Mta_As_Alice_Users_Data.user_index == user_index
            ).update({"commitment_of_a": commitment_of_a.to_dict()})  # Convert to dict inside the DAL
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Alice's commitment for transaction {transaction_id}: {e}")
            return False

def update_bobs_challenge(transaction_id: str, user_index: int, bobs_challenge: int) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Alice_Users_Data).filter(
                Mta_As_Alice_Users_Data.transaction_id == transaction_id,
                Mta_As_Alice_Users_Data.user_index == user_index
            ).update({"bobs_challenge": bobs_challenge})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's challenge for transaction {transaction_id}: {e}")
            return False

def update_bobs_encrypted_value_and_commitment(transaction_id: str, user_index: int, bobs_encrypted_value: EncryptedNumber, 
                                                bobs_commitment: Bob_ZKProof_ProverCommitment) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Alice_Users_Data).filter(
                Mta_As_Alice_Users_Data.transaction_id == transaction_id,
                Mta_As_Alice_Users_Data.user_index == user_index
            ).update({
                "bobs_encrypted_value": serialize_encryped_number(bobs_encrypted_value),  # Convert EncryptedNumber
                "bobs_commitment": bobs_commitment.to_dict()  # Convert Commitment
            })
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's encrypted response and commitment for transaction {transaction_id}: {e}")
            return False


def update_alice_challenge(transaction_id: str, user_index: int, alice_challenge: int) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Alice_Users_Data).filter(
                Mta_As_Alice_Users_Data.transaction_id == transaction_id,
                Mta_As_Alice_Users_Data.user_index == user_index
            ).update({"alice_challenge": alice_challenge})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Alice's challenge for transaction {transaction_id}: {e}")
            return False

def update_bob_proof_for_challenge(transaction_id: str, user_index: int, bob_proof_for_challenge: Bob_ZKProof_Proof_For_Challenge) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Alice_Users_Data).filter(
                Mta_As_Alice_Users_Data.transaction_id == transaction_id,
                Mta_As_Alice_Users_Data.user_index == user_index
            ).update({"bob_proof_for_challenge": bob_proof_for_challenge.to_dict()})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's proof for Alice's challenge for transaction {transaction_id}: {e}")
            return False

# ================================================================================================
# MTA Protocl Methods - When the user is in Bob's shoes. The relevant steps are:
# 1. Store enc_a  and a's commitment
# 2. Store Bob's Challenge
# 3. Store Bob's Encrypted Response & Bob's Commitment and finally beta_prime
# 5. Store Bob's Proof for challenge - After getting challenge by alice
# 6. Store Bob's Proof for Alice's challenge (mainly for tracking...)
# ================================================================================================

def insert_mta_as_bob(transaction_id: str, user_index: int, counterparty_index: int, enc_a: EncryptedNumber, commitment_of_a: AliceZKProof_Commitment) -> bool:
    with DB.session() as session:
        try:
            entry = Mta_As_Bob_Users_Data(
                transaction_id=transaction_id,
                user_index=user_index,
                counterparty_index=counterparty_index,
                enc_a=serialize_encryped_number(enc_a),
                commitment_of_a=commitment_of_a.to_dict()  # Serialize Commitment
            )
            session.add(entry)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to insert MtA (as Bob) for transaction {transaction_id}: {e}")
            return False

def update_bobs_challenge(transaction_id: str, user_index: int, bobs_challenge: int) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Bob_Users_Data).filter(
                Mta_As_Bob_Users_Data.transaction_id == transaction_id,
                Mta_As_Bob_Users_Data.user_index == user_index
            ).update({"bobs_challenge": bobs_challenge})

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's challenge for transaction {transaction_id}: {e}")
            return False

def update_bobs_encrypted_value_and_commitment(transaction_id: str, user_index: int, enc_result: EncryptedNumber, 
                                                bobs_commitment: Bob_ZKProof_ProverCommitment, beta_prime: int) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Bob_Users_Data).filter(
                Mta_As_Bob_Users_Data.transaction_id == transaction_id,
                Mta_As_Bob_Users_Data.user_index == user_index
            ).update({
                "enc_result": serialize_encryped_number(enc_result),
                "bobs_commitment": bobs_commitment.to_dict(),  # Serialize Commitment
                "beta_prime": beta_prime})

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's encrypted result for transaction {transaction_id}: {e}")
            return False

def update_bob_proof_for_challenge(transaction_id: str, user_index: int, bob_proof_for_challenge: Bob_ZKProof_Proof_For_Challenge) -> bool:
    with DB.session() as session:
        try:
            session.query(Mta_As_Bob_Users_Data).filter(
                Mta_As_Bob_Users_Data.transaction_id == transaction_id,
                Mta_As_Bob_Users_Data.user_index == user_index
            ).update({"bob_proof_for_challenge": bob_proof_for_challenge.to_dict()})  # Serialize Proof

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update Bob's proof for transaction {transaction_id}: {e}")
            return False

def get_mta_as_bob(transaction_id: str, user_index: int, counterparty_index: int) -> Mta_As_Bob_Users_Data:
    with DB.session() as session:
        record = session.query(Mta_As_Bob_Users_Data).filter(
            Mta_As_Bob_Users_Data.transaction_id == transaction_id,
            Mta_As_Bob_Users_Data.user_index == user_index,
            Mta_As_Bob_Users_Data.counterparty_index == counterparty_index).first()

        if not record:
            print(f"Couldn't find mta_as_bob data for target user {counterparty_index} for transaction {transaction_id}")
            return None
        
        record.enc_a = EncryptedNumber.from_dict(record.enc_a) if record.enc_a else None
        record.commitment_of_a = AliceZKProof_Commitment.from_dict(record.commitment_of_a) if record.commitment_of_a else None
        record.enc_result = EncryptedNumber.from_dict(record.enc_result) if record.enc_result else None
        record.bobs_commitment = Bob_ZKProof_ProverCommitment.from_dict(record.bobs_commitment) if record.bobs_commitment else None
        record.bob_proof_for_challenge = Bob_ZKProof_Proof_For_Challenge.from_dict(record.bob_proof_for_challenge) if record.bob_proof_for_challenge else None

        return record
