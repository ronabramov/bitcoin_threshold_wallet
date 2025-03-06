from local_db import sql_db_dal
from local_db.sql_db import Wallet
import random
from ecdsa import curves
from models.protocols.Commitment import commit_x
import json
from APIs.Algorithm_Steps_Implementation.StepTwo import StepTwo_SendAliceMtaMessages
from models.commitment import Commitment
from models.algorithm_step import Algorithm_Step
from APIs.RoomManagementAPI import send_private_message_to_every_user_in_Wallet
from phe import paillier

class StepOne_PrepareDataForMta:
    def execute(self, wallet : Wallet) -> bool:
        """
        Choose u.a.r k_i, gamma_i. 
        Share g^{gamma_i} for every participating user.
        """
        curve = curves.curve_by_name(wallet.curve_name)
        q = curve.order
        gamma_i = random.randint(0, q)
        k_i = random.randint(0, q)
        # save k_i, gamma_i to db
        G = curve.generator
        commitment = gamma_i * G
        json_wallet_configuration = json.loads(wallet.configuration)
        encrypted_commitment = commit_x(json_wallet_configuration["paillier_public_key"], commitment)
        # send commitment to all users
        n = json_wallet_configuration["paillier_public_key"]["n"]
        #TODO - check if this is the correct way to get my user data
        my_user_data = sql_db_dal.get_my_wallet_user_data(wallet.wallet_id)
        commitment_message = Commitment(algorithm_step=Algorithm_Step.SIGNATURE_PHASE_ONE, 
                                        committing_user_index=my_user_data.user_index, 
                                        committed_values=[encrypted_commitment], 
                                        committing_user_paillier_public_key= paillier.PaillierPublicKey(n= n))
        send_private_message_to_every_user_in_Wallet(commitment_message, wallet.wallet_id)
        StepTwo_SendAliceMtaMessages.execute(wallet, k_i, gamma_i, my_user_data, curve)
        

        
