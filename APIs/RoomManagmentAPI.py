import local_db.sql_db_dal as db_dal
from local_db.sql_db import User, Wallet, Friend, Room_User_Data
from Services.MatrixService import MatrixService
from typing import Dict, Optional, List
from DTOs.message_dto import MessageDTO
from models.models import user_public_share, WalletGenerationMessage
import common_utils as Utils
from ecdsa import NIST256p, curves
from APIs.Algorithm_Steps_Implementation.user_signature_generation import UserSignatureGenerator


GENERATING_USER_INDEX = 1

def get_all_friends():
    return db_dal.get_all_user_friends()

def get_all_new_invitations():
    return MatrixService.instance().fetch_pending_invited_rooms()

def respond_to_room_invitation(room_id : str, user_accepted_invitation : bool):
    if not user_accepted_invitation:
        MatrixService.instance().reject_room_invitation_by_id(room_id=room_id)
    
    room_name = MatrixService.instance().join_room_invitation(room_id=room_id)
    if is_wallet_room(room_name):
        result = handle_joining_new_wallet(room_name=room_name, room_id=room_id)
        return result

def handle_joining_new_wallet(user_id : str, room_name : str, room_id : str) -> bool:
    """
    Should create Transaction_Room (db) object including mapping of other users public shares. 
    """
    user_index_in_wallet = MatrixService.instance().get_next_available_index()
    room_messages = MatrixService.instance().get_valid_json_messages(room_id=room_id)

    user_room_secret_data, user_public_data = Utils.generate_user_room_keys(user_index=user_index_in_wallet, user_matrix_id=user_id)

    generation_wallet_msg  = [msg for msg in room_messages if msg.type == WalletGenerationMessage.get_type()][0]
    existing_users_shares_messages : list[user_public_share] = [user_msg.data for user_msg in room_messages if user_msg.type == user_public_share.get_type()]
    participating_users = ",".join([msg.user_id for msg in existing_users_shares_messages])
    wallet = get_wallet_from_generating_wallet_message(wallet_id=room_id, wallet_participants=participating_users, generation_message=generation_wallet_msg)
    signature_created = handle_wallet_signature(wallet=wallet, user_public_share=user_public_data, existing_users_in_wallet=existing_users_shares_messages)
    if not signature_created:
        print (f"Failed generating wallet's signature")
        return False
    
    insertion_succeded = db_dal.insert_new_wallet(wallet=wallet)
    if not insertion_succeded:
        print (f"Failed saving wallet to local db")
        return False
    
    insertion_succeded = save_room_users_data_to_db(room_id=room_id, generating_wallet_message=generation_wallet_msg, rest_users_messages=existing_users_shares_messages)
    if not insertion_succeded:
        print (f"Failed saving room_users_data to local db")
        return False
    
    public_keys_message = MessageDTO(type=user_public_share.get_type(), data=user_public_data).model_dump_json()
    message_sent = MatrixService.instance().send_message_to_wallet_room(room_id=room_id, message=public_keys_message)
    if not message_sent:
        print(f' Failed sending joining message to wallet room.')

    return True

def get_wallet_from_generating_wallet_message(wallet_id : str, wallet_participants : str, generation_message : WalletGenerationMessage) -> Wallet:
    return Wallet(wallet_id=wallet_id, threshold = generation_message.threshold, users=wallet_participants,
                  curve_name = generation_message.curve_name, max_num_of_users = generation_message.max_number_of_participants)

def save_room_users_data_to_db(wallet_id: str, rest_users_messages: list[user_public_share]) -> bool:

    success = True
    for user_message in rest_users_messages:
        result = db_dal.insert_new_room_user(
            wallet_id=wallet_id,
            user_index=user_message.user_index,
            user_matrix_id=user_message.user_id,
            user_public_keys=user_message
        )
        if not result:
            success = False  # If any insertion fails, mark as failure

    return success


def create_new_wallet(user_id : str, invited_users_emails : List[str], wallet_name : str, wallet_threshold : int,
                       max_participants : int, curve_name : str = NIST256p.name ):
    """
    Creating matrix room and sending invitaiton for the specified users. 
    In addition, sharing Public keys of the generating user.
    """
    wallet_generation_message = MessageDTO(type = WalletGenerationMessage.get_type(), 
                                           data=WalletGenerationMessage(threshold=wallet_threshold, curve_name=curve_name)).model_dump_json()
    
    users_ids : list[Friend] = [db_dal.get_friend_by_email(email=email).matrix_id for email in invited_users_emails]
    room_id = MatrixService.instance().create_new_room_and_invite_users(room_name=wallet_name, users_Ids=users_ids, first_message=wallet_generation_message)
    if not room_id:
        print('Failure in room creation - Matrix service failed to create room')
        return False, None
    
    #Every user will add user to his wallet only when user has been joined
    wallet = Wallet(wallet_id=room_id,threshold=wallet_threshold,users="", curve_name = curve_name) 
    user_room_secret_data, user_room_public_data = Utils.generate_user_room_keys(user_index=GENERATING_USER_INDEX,
                                                                                             user_matrix_id=user_id, curve_name=curve_name)
    
    signature_created = handle_wallet_signature(wallet=wallet, user_keys=user_room_public_data)
    
    if not signature_created:
        print(f'Failed Generating signature data for wallet {wallet.wallet_id}')
        return False, None
    
    insertion_succeded = db_dal.insert_new_wallet(wallet=wallet)
    if not insertion_succeded:
        print (f"Failed saving wallet to local db")
        return False, None
    
    public_keys_message = MessageDTO(type=user_public_share.get_type(), data=user_room_public_data).model_dump_json()
    message_sent = MatrixService.instance().send_message_to_wallet_room(room_id=room_id, message=public_keys_message)
    return insertion_succeded and message_sent, wallet

def handle_wallet_signature(wallet : Wallet, user_keys : user_public_share, existing_users_in_wallet : list[user_public_share] = None) -> bool:
    signature_generator = UserSignatureGenerator(wallet=wallet,  user_public_keys=user_keys)
    signature_flow_is_valid = signature_generator.handle_key_generation_for_user()
    if signature_flow_is_valid and existing_users_in_wallet is not None :
        signature_flow_is_valid = signature_generator.handle_existing_users_signatures(existing_users_keys=existing_users_in_wallet)
    return signature_flow_is_valid
    
def is_wallet_room(room_name : str):
    #TODO:implement. 
    return True