from models.protocols.Feldman_VSS_protocol import Feldman_VSS_Protocol
from ecdsa import NIST256p, curves
from models.protocols.ShareShrinker import ShareShrinker
import random
from local_db.sql_db import Wallet
import local_db.sql_db_dal as DB_DAL
from models.models import user_secret_signature_share, key_generation_share, user_modulus, user_public_share
import APIs.UserToUserAPI 
import Services.UserShareService as UserShareService
import local_db.sql_db_dal as sql_dal

class UserSignatureGenerator:
    def __init__(self, wallet : Wallet, user_public_keys : user_public_share):
        curve = curves.curve_by_name(wallet.curve_name)
        self.wallet_id = wallet.wallet_id
        self.key_gen_protocol = Feldman_VSS_Protocol(n=wallet.max_num_of_users, t=wallet.threshold, curve=curve, generating_user_Index=user_public_keys.user_index)
        self.q = curve.order
        self.curve = curve
        self.n =wallet.max_num_of_users
        self.t = wallet.threshold   
        self.user_public_keys = user_public_keys
        self.wallet = wallet
        self.user_index = user_public_keys.user_index

    def handle_key_generation_for_user(self):
        """
        1. Generates signature for user. Update Wallet secret with signature data
        2. Records signature shares in DB        """
        user_key_generation_participants_shares, user_secret = self.generate_secret_and_shares_for_other_users()
        self.enrich_user_secret_data_with_signature_details(secret=user_secret, share = user_key_generation_participants_shares[self.user_public_keys.user_index])
        insertion_success = DB_DAL.insert_multiple_signature_shares(wallet_id=self.wallet_id, shares= list(user_key_generation_participants_shares.values()))
        return insertion_success

    def enrich_user_secret_data_with_signature_details(self, secret : int, share : key_generation_share):
        wallet_secret = self.wallet.get_room_secret_user_data()
        wallet_secret.original_secret_share = secret
        wallet_secret.original_secret_share = share.target_user_evaluation
        wallet_secret.num_of_updates = 0
        self.wallet.set_room_secret_user_data(wallet_secret)

    def generate_secret_and_shares_for_other_users(self):
        secret = random.randint(1, self.q - 1)
        shares = self.key_gen_protocol.generate_shares(secret=secret)
        shares_dict = {share.target_user_index: share for share in shares}
        return shares_dict, secret
    
    def  handle_existing_users_signatures(self, existing_users_keys : list[user_public_share]):
        shares_dict = {}
        users_signature_shares = DB_DAL.get_signature_shares_by_wallet(self.wallet_id)
        for user in existing_users_keys:
            if user.user_index == self.user_index:
                continue # Send Messages only for other users
            user_share = UserShareService.filter_shares_by_user_index(users_signature_shares, user.user_index)
            user_share.target_user_matrix_id = user.user_id
            #Better update that entity in DB. RON like that: (?)
            sql_dal.update_signature_share(self.wallet_id, user_share)
            shares_dict[user.user_index] = user_share

        return self.send_share_for_every_participating_user(shares_dict=shares_dict)

    
    def send_share_for_every_participating_user(self, shares_dict : dict) -> bool:
        success = APIs.UserToUserAPI.bulk_send_key_share(list(shares_dict.values()))
        return success
    
    def apply_received_share(self, user_share : user_secret_signature_share, peer_share : key_generation_share):
        validated_share = self.validate_peer_share(peer_share=peer_share)
        if not validated_share:
            # TODO: maybe keep print(f'User {peer_share.generating_user_index} sent unvalid key share!')
            raise ValueError(f'User {peer_share.generating_user_index} sent unvalid key share!')
        user_share.user_evaluation += peer_share.target_user_evaluation
        return user_share
    
    def validate_peer_share(self, peer_share : key_generation_share):
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