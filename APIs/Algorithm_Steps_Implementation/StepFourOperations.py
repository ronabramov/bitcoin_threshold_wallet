from phe import EncryptedNumber
import local_db.sql_db_dal as db_Dal
from models.protocols.Commitment import decommit_value
from ecdsa.curves import curve_by_name, Curve
from ecdsa.ellipticcurve import PointJacobi
from models.protocols.Schnorr_ZKProof import Schnorr_ZK_Proof
from common_utils import sum_jacobi_points


class StepFourOperations:
    def broadcast_decommited_g_power_gamma_i(commited_value : EncryptedNumber, transaction_id : str, wallet_id : str, user_index : int):
        #Here we broadcast out decommited value to other users
        paillier_secret = db_Dal.get_wallet_by_id(wallet_id=wallet_id).get_room_secret_user_data().paillier_secret_key
        decommited_g_pow_gamma_i = decommit_value(private_key=paillier_secret, value=commited_value)
        curve = curve_by_name(db_Dal.get_wallet_by_id(wallet_id=wallet_id).curve_name)
        zk_proof_generator = Schnorr_ZK_Proof(curve=curve)
        gamma_i = db_Dal.get_my_user_gamma(wallet_id=wallet_id)
        proof_of_knowledge = zk_proof_generator.provide_zk_proof_for_input(gamma_i)
        # RON TODO : generated a message type for these values. 
        db_Dal.insert_user_gamma_i_step_four(gamma_i=gamma_i, wallet_id=wallet_id, user_index=user_index, transaction_id=transaction_id)
    
    def calculate_R_and_r(delta_inv : int, transaction_id : str, wallet_id : str):
        q = curve_by_name(db_Dal.get_wallet_by_id(wallet_id=wallet_id).curve_name).order
        users_gammas = db_Dal.get_users_gamma_shares_by_transaction_id(transaction_id=transaction_id)
        multiplied_gammas = sum_jacobi_points(points = users_gammas)
        R = multiplied_gammas * delta_inv
        r = R.x() % q #r = H'(R) which is defined in the paper as R_x mod q.
        return (R,r)


    
