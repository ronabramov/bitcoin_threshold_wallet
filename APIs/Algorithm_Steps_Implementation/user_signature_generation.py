from protocols.Feldman_VSS_protocol import Feldman_VSS_Protocol
from ecdsa import NIST256p, curves
import random
from models.models import user_signature_share
from APIs.UserToUserAPI import send_key_share_for_participating_users

class user_signature_generator:
    def __init__(self, modulus : int, curve : curves.Curve, n :int , t : int, user_index : int, user_index_to_user_matrixId : dict):
        self.key_gen_protocol = Feldman_VSS_Protocol(n=n, t=t, curve=curve)
        self.user_index = user_index
        self.q = curve.order
        self.user_index_to_user_matrixId = user_index_to_user_matrixId
        self.curve = curve
        self.modulus = modulus
        self.n =n

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
        success = send_key_share_for_participating_users(list(shares_dict.values()))
        return success