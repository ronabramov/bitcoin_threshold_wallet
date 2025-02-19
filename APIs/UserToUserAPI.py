from models.models import key_generation_share
from typing import List
from models.DTOs.message_dto import MessageDTO, MessageType
from Services.MatrixService import MatrixService

MAX_RETRIES = 3

"""
This is the APIs the controller should reach for any user-to-user services
Methods:
1. send_key_share_for_participating_users
2. 
"""

def bulk_send_key_share(Shares : List[key_generation_share]) -> bool:
    """
    Send private message for every participating user with it's share.
    """
    
    success = False
    for key_share in Shares:
        try:
            send_key_share(key_share)        
            success = True
        except Exception as e:
            print(f'Failed sending message to user {key_share.target_user_index}, with matrix_id : {key_share.target_user_matrix_id}', e)
    
    return success

def send_key_share(key_share : key_generation_share) -> bool:
    tries = 0
    while tries <= MAX_RETRIES:
        try:
            message_to_user = MessageDTO(type=MessageType.KeyGenerationShare, data=key_share).model_dump_json()
            MatrixService.instance().send_private_message_to_user(target_user_matrix_id=key_share.target_user_matrix_id, message=message_to_user)
            return True
        except Exception as e:
            print(f'Failed sending message to user {key_share.target_user_matrix_id}', e)
            tries += 1
    
    raise Exception(f'Max retries reached for sending message to user {key_share.target_user_matrix_id}')
        