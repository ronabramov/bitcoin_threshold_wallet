from local_db import sql_db_dal
from APIs import UserToUserAPI
from models.models import user_public_share, key_generation_share

# TODO: RON - check if this is the correct way to handle the incoming public share
def handle_incoming_public_share(incoming_user_public_share : user_public_share, wallet_id : str):
    sql_db_dal.get_wallet_by_id(wallet_id)
    # 2 we need to save this user data locally (room user data)
    sql_db_dal.insert_new_room_user(wallet_id, incoming_user_public_share.user_index, incoming_user_public_share.user_id, incoming_user_public_share)
    # 3 get signature by wallet
    users_signature_shares = sql_db_dal.get_signature_shares_by_wallet(wallet_id)
    # 4 find share of user by its index
    user_share = filter_shares_by_user_index(users_signature_shares, incoming_user_public_share.user_index)
    # 5 upsert user index to this share
    user_share.target_user_matrix_id = incoming_user_public_share.user_id
    # 6 update share in db
    sql_db_dal.update_signature_share(wallet_id, user_share)
    # 7 send key share for participating user
    UserToUserAPI.send_key_share(user_share)
    
def filter_shares_by_user_index(shares : list[key_generation_share], user_index : int) -> key_generation_share:
    return next(share for share in shares if share.target_user_index == user_index)