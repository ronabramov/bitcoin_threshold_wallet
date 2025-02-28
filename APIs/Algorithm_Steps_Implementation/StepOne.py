from local_db import sql_db_dal
import random
from ecdsa import curves
from models.protocols.Commitment import commit_x
import json
from APIs.Algorithm_Steps_Implementation.StepTwo import StepTwo

class StepOne:
    def execute(self, wallet_id : str):
        wallet = sql_db_dal.get_wallet_by_id(wallet_id)
        # get curve 
        curve = curves.curve_by_name(wallet.curve_name)
        q = curve.order -1
        # select u.a.r k_i,  from Z_q
        gamma_i = random.randint(0, q)
        # select u.a.r gamma_i from Z_q
        k_i = random.randint(0, q)
        # save k_i, gamma_i to db
        G = curve.generator
        commitment = gamma_i * G
        json_wallet_configuration = json.loads(wallet.configuration)
        encrypted_commitment = commit_x(json_wallet_configuration["paillier_public_key"], commitment)
        StepTwo.execute(wallet_id, k_i, gamma_i)
        
        
