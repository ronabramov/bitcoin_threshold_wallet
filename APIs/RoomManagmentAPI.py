import local_db.sql_db_dal as db_dal
from local_db.sql_db import User, Wallet, Friend
from Services.MatrixService import MatrixService
from typing import Dict, Optional, List
from DTOs.message_dto import MessageDTO
from models.models import room_public_user_data
import common_utils as Utils

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

def handle_joining_new_wallet(room_name : str, room_id : str):
    user_index_in_wallet = MatrixService.instance().get_next_available_index()
    # TODO : 
    # 1. Get indecis of existing users and their public keys.
    # 2. Share your index and public key in room.
    # r. Save wallet in local_db with it's secret key- see create_new_wallet for example.
    return False

def create_new_wallet(user_id : str, invited_users_emails : List[str], wallet_name : str, wallet_threshold : int):
    """
    Creating matrix room and sending invitaiton for the specified users. 
    In addition, sharing Public keys of the generating user.
    """
    users_ids : list[Friend] = [db_dal.get_friend_by_email(email=email).matrix_id for email in invited_users_emails]
    room_id = MatrixService.instance().create_new_room_and_invite_users(room_name=wallet_name, users_Ids=users_ids)
    if not room_id:
        print('Failure in room creation - Matrix service failed to create room')
        return False, None
    
    wallet = Wallet(wallet_id=room_id,threshold=wallet_threshold,users=",".join(users_ids))
    insertion_succeded = db_dal.insert_new_wallet(wallet=wallet)
    if not insertion_succeded:
        print (f"Failed saving wallet to local db")
        return False, None
    
    user_room_secret_data, user_room_public_data = Utils.generate_user_room_keys(user_index=GENERATING_USER_INDEX, user_matrix_id=user_id)
    wallet.set_room_secret_user_data(data=user_room_secret_data)
    public_keys_message = MessageDTO(type=room_public_user_data.get_type(), data=user_room_public_data).model_dump_json()
    message_sent = MatrixService.instance().send_message_to_wallet_room(room_id=room_id, message=public_keys_message)
    return insertion_succeded and message_sent, wallet
    
def is_wallet_room(room_name : str):
    #TODO:implement.
    return