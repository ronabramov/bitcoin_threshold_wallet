from protocols.Feldman_VSS_protocol import Feldman_VSS_Protocol
from ecdsa import NIST256p, curves
from protocols.ShareShrinker import ShareShrinker
import random
from models.models import user_signature_share, user_key_generation_share
import APIs.UserToUserAPI 

class user_signature_generator:
    def __init__(self, modulus : int, curve : curves.Curve, n :int , t : int, user_index : int,
                  user_index_to_user_matrixId : dict, participating_users_indecis : list):
        self.key_gen_protocol = Feldman_VSS_Protocol(n=n, t=t, curve=curve)
        self.user_index = user_index
        self.q = curve.order
        self.user_index_to_user_matrixId = user_index_to_user_matrixId
        self.curve = curve
        self.modulus = modulus
        self.n =n
        self.participating_users_indecis = participating_users_indecis

    def generate_secret_and_shares_for_other_users(self):
        secret = random.randint(1, self.q - 1)
        shares = self.key_gen_protocol.generate_shares(secret=secret)
        shares_dict = {share['index']: share for share in shares}
        user_share = shares_dict[self.user_index]

        my_share = user_signature_share(self.user_index, self.user_index_to_user_matrixId[self.user_index], 
                                        user_evaluation=user_share.target_user_evaluation, group=self.curve,modulus_N=self.modulus)
        shares_dict.__delitem__(self.user_index)
        return my_share, shares_dict
    
    def send_share_for_every_participating_user(self, shares_dict : dict) -> bool:
        for i in range(1,self.n+1):
            if i == self.user_index : 
                continue
        success = APIs.UserToUserAPI.send_key_share_for_participating_users(list(shares_dict.values()))
        return success
    
    def apply_received_share(self, user_share : user_signature_share, peer_share : user_key_generation_share):
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
    
    def get_user_shrinked_secret(self, user_share : user_signature_share):
        """
        After all users passed their shares, we generate from the user_evaluation
        a shrinked (t,t+1) share of x.
        """
        secret_shrinker = ShareShrinker(q=self.q, i=self.user_index, x_i=user_share.user_evaluation, S = self.participating_users_indecis)
        shrinked_share = secret_shrinker.compute_new_share()
        user_share.shrinked_secret_share = shrinked_share
        return user_share