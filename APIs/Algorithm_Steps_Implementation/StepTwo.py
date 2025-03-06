from local_db.sql_db import Wallet, WalletUserData
import local_db.sql_db_dal as db_dal
from models.models import user_modulus, user_public_share
from models.protocols.mta_protocol import MTAProtocolWithZKP
from models.protocols.MtaWc_protocl import MtaWcProtocolWithZKP
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment
from ecdsa.curves import Curve
from ecdsa.ellipticcurve import PointJacobi
from models.DTOs import message_dto, MessageType


class StepTwo_SendAliceMtaMessages:
    def execute(self, wallet : Wallet, k_i : int, gamma_i : int, sending_user_data : WalletUserData, curve : Curve):
        """
        In that stage we need to send for every user our Mta message as alice. 
        Moreover, we want to prepare all the relevant data in the DB
        for the rest of the Mta and MtaWC algorithms.
        """
        user_secret_data = wallet.get_room_secret_user_data()
        wallet_users_public_shares = db_dal.get_all_wallet_user_data(wallet_id=wallet.wallet_id)
        sending_user_public_share = user_public_share.from_dict(sending_user_data.user_public_keys_data)
        for destination_user_data in wallet_users_public_shares:
            destination_user_public_share = user_public_share.from_dict(destination_user_data.user_public_keys_data)
            destination_user_public_key = PointJacobi() #RON TODO : deserialize the destinatoin user public key
            mta_protocol = MTAProtocolWithZKP(alice_public_share=sending_user_public_share, bob_public_share=destination_user_public_share, curve=curve,
                                              bob_public_g_power_secret=destination_user_public_key, b_value=None,
                                                alice_paillier_private_key=user_secret_data.paillier_secret_key)
            
            mta_wc_settings = MtaWcProtocolWithZKP(alice_public_share=sending_user_data, bob_public_share=destination_user_public_share, curve=curve,
                                                   bob_public_g_power_secret=destination_user_public_key,
                                                     b_value=None, alice_paillier_private_key=user_secret_data.paillier_secret_key)
            
            mta_enc_ki, mta_commitment_of_ki = mta_protocol.alice_encrypting_a_and_sending_commitment(a=k_i, alice_paillier_public_key=user_secret_data.paillier_public_key)
            # mta_commitment_message = 
            return
    