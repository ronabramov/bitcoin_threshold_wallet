from models.models import key_generation_share

def filter_shares_by_user_index(shares : list[key_generation_share], user_index : int):
    return next((share for share in shares if share.target_user_index == user_index), None)
