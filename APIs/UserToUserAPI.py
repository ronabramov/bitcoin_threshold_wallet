from models.models import user_key_generation_share
from typing import List
from models.DTOs.message_dto import MessageDTO
from Services.MatrixService import MatrixService

MAX_RETRIES = 3

"""
This is the APIs the controller should reach for any user-to-user services
Methods:
1. send_key_share_for_participating_users
2. 
"""

def send_key_share_for_participating_users(Shares : List[user_key_generation_share]) -> bool:
    """
    Send private message for every participating user with it's share.
    """
    users_dont_got_message = [share.target_user_index for share in Shares]
    tries = 0
    while tries <= MAX_RETRIES and users_dont_got_message.count() > 0: 
        for key_share in Shares:
            message_to_user = MessageDTO(type=user_key_generation_share.get_type(), data=key_share)
            try:
                success = MatrixService.instance().send_private_message_to_user(target_user_matrix_id=key_share.target_user_matrix_id, message=message_to_user)
                if success:
                    users_dont_got_message.remove(key_share.target_user_index)
            except Exception as e:
                print(f'Failed sending message to user {key_share.target_user_index}, with matrix_id : {key_share.target_user_matrix_id}', e)

    return users_dont_got_message.count() == 0