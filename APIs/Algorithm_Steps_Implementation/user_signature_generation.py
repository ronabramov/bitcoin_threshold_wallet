from models.protocols.Feldman_VSS_protocol import Feldman_VSS_Protocol
from ecdsa import NIST256p, curves
from models.protocols.ShareShrinker import ShareShrinker
import random
from local_db.sql_db import Wallet
import local_db.sql_db_dal as DB_DAL
from models.models import user_secret_signature_share, user_key_generation_share, user_modulus, user_public_share
import APIs.UserToUserAPI 

class UserSignatureGenerator:
    def __init__(self, wallet : Wallet, user_public_keys : user_public_share):
        curve = curves.curve_by_name(wallet.curve_name)
        self.wallet_id = wallet.wallet_id
        self.key_gen_protocol = Feldman_VSS_Protocol(n=wallet.max_num_of_users, t=wallet.threshold, curve=curve)
        self.q = curve.order
        self.curve = curve
        self.n =wallet.max_num_of_users
        self.t = wallet.threshold   
        self.user_public_keys = user_public_keys

    def generate_and_save_shares(self):
        user_key_generation_participants_shares = self.generate_secret_and_shares_for_other_users()
        insertion_success = DB_DAL.insert_multiple_signature_shares(wallet_id=self.wallet_id, shares= list(user_key_generation_participants_shares.values()))
        return insertion_success


    def generate_secret_and_shares_for_other_users(self):
        secret = random.randint(1, self.q - 1)
        shares = self.key_gen_protocol.generate_shares(secret=secret)
        shares_dict = {share['index']: share for share in shares}
        return shares_dict
    
    def send_share_for_every_participating_user(self, shares_dict : dict) -> bool:
        success = APIs.UserToUserAPI.send_key_share_for_participating_users(list(shares_dict.values()))
        return success
    
    def apply_received_share(self, user_share : user_secret_signature_share, peer_share : user_key_generation_share):
        validated_share = self.validate_peer_share(peer_share=peer_share)
        if not validated_share:
            print(f'User {peer_share.generating_user_index} sent unvalid key share!')
        user_share.user_evaluation += peer_share.target_user_evaluation
        return user_share
    
    def validate_peer_share(self, peer_share : user_key_generation_share):
        peer_user_protocol = Feldman_VSS_Protocol(self.n, self.t, peer_share.transaction_id, self.user_index_to_user_matrixId,
                                                   generating_user_Index=peer_share.generating_user_index, curve=peer_share.curve)
        is_valid = peer_user_protocol.verify_share(peer_share)
        return is_valid
    
    def get_user_shrinked_secret(self, user_share : user_secret_signature_share):
        """
        After all users passed their shares, we generate from the user_evaluation
        a shrinked (t,t+1) share of x.
        """
        secret_shrinker = ShareShrinker(q=self.q, i=self.user_index, x_i=user_share.user_evaluation, S = self.participating_users_indecis)
        shrinked_share = secret_shrinker.compute_new_share()
        user_share.shrinked_secret_share = shrinked_share
        return user_share