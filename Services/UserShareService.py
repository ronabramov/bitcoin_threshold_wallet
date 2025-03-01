from local_db import sql_db_dal
from APIs import UserToUserAPI

from APIs.Algorithm_Steps_Implementation.user_signature_generation import UserSignatureGenerator
from models.models import user_public_share, wallet_key_generation_share
from Services.UserShareUtils import filter_shares_by_user_index
from models.models import user_public_share, wallet_key_generation_share
from APIs.Algorithm_Steps_Implementation.user_signature_generation import UserSignatureGenerator


def handle_incoming_public_share(incoming_user_public_share : user_public_share, wallet_id : str):
    sql_db_dal.get_wallet_by_id(wallet_id)
    sql_db_dal.insert_new_wallet_user_data(wallet_id, incoming_user_public_share.user_index, incoming_user_public_share.user_id, incoming_user_public_share)
    users_signature_shares = sql_db_dal.get_signature_shares_by_wallet(wallet_id)
    user_key_generation_share = filter_shares_by_user_index(users_signature_shares, incoming_user_public_share.user_index)
    if not user_key_generation_share:
        print(f"ERROR : No share found for user index {incoming_user_public_share.user_index}")
        raise FileNotFoundError(f'ERROR : No share found for user index {incoming_user_public_share.user_index}')
    
    user_key_generation_share.target_user_matrix_id = incoming_user_public_share.user_id
    sql_db_dal.update_signature_share(wallet_id, user_key_generation_share)
    UserToUserAPI.send_key_share(user_key_generation_share)


def handle_incoming_key_generation_share(key_generation_share_obj : wallet_key_generation_share):
    print(f"Key generation share received: {key_generation_share_obj}")
    wallet = sql_db_dal.get_wallet_by_id(key_generation_share_obj.wallet_id)
    user_secret = wallet.get_room_secret_user_data()
    if not user_secret:
        print(f"User share not found in the wallet")
        return
    signature_generator = UserSignatureGenerator(wallet=wallet,  user_public_keys=user_secret)
    
    user_secret = signature_generator.aggregate_received_share(peer_share=key_generation_share_obj, user_secret=user_secret)
    if not user_secret:
        print(f"Failed applying received share")
    else:
        print(f"User share applied successfully")
        sql_db_dal.update_signature_share(key_generation_share_obj.wallet_id, user_secret)
        
        
    return