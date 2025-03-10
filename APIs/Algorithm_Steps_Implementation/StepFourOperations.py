from phe import EncryptedNumber
import local_db.sql_db_dal as db_Dal
from models.protocols.Commitment import decommit_value
from ecdsa.curves import curve_by_name, Curve
from models.protocols.Schnorr_ZKProof import Schnorr_ZK_Proof

class StepFourOperations:
    def broadcast_decommited_g_power_gamma_i(commited_value : EncryptedNumber, transaction_id : str, delta_inv : int , wallet_id : str):
        #Here we broadcast out decommited value to other users
        paillier_secret = db_Dal.get_wallet_by_id(wallet_id=wallet_id).get_room_secret_user_data().paillier_secret_key
        decommited_g_pow_gamma_i = decommit_value(private_key=paillier_secret, value=commited_value)
        curve = curve_by_name(db_Dal.get_wallet_by_id(wallet_id=wallet_id).curve_name)
        zk_proof_generator = Schnorr_ZK_Proof(curve=curve)
        # RON TODO : gamma_i = get value from db
        gamma_i = 1
        proof_of_knowledge = zk_proof_generator.provide_zk_proof_for_input(gamma_i)
        # RON TODO : generated a message type for these values. 