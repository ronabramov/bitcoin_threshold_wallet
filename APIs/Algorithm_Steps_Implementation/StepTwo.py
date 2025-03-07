from local_db.sql_db import Wallet, WalletUserData
import local_db.sql_db_dal as db_dal
from models.models import user_modulus, user_public_share, user_secret_signature_share, GPowerX
from models.protocols.mta_protocol import MTAProtocolWithZKP
from models.protocols.MtaWc_protocl import MtaWcProtocolWithZKP
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_ProverCommitment, Bob_ZKProof_Proof_For_Challenge
from ecdsa.curves import Curve, curve_by_name
from ecdsa.ellipticcurve import PointJacobi
from models.DTOs.MessageType import MessageType
from models.DTOs.message_dto import MessageDTO
from Services.MatrixService import MatrixService
from phe import EncryptedNumber



class StepTwo_Mta_And_MtaWc:
    
    def send_alice_mta_encryptions_and_commitment(self, wallet : Wallet, k_i : int, gamma_i : int, sending_user_data : WalletUserData, curve : Curve, transaction_id : str):
        """
        In that stage we need to send for every user our Mta message as alice. 
        Moreover, we want to prepare all the relevant data in the DB
        for the rest of the Mta and MtaWC algorithms.
        """
        user_secret_data = wallet.get_room_secret_user_data()
        wallet_users_public_shares = db_dal.get_all_wallet_user_data(wallet_id=wallet.wallet_id)
        sending_user_public_share = user_public_share.from_dict(sending_user_data.user_public_keys_data)
        for destination_user_data in wallet_users_public_shares:
            destination_user_share = user_public_share.from_dict(destination_user_data.user_public_keys_data)
            StepTwo_Mta_And_MtaWc.create_and_send_Ki_mta_commitment(sending_user_public_share=sending_user_public_share, curve=curve,
                                                                            user_secret_data=user_secret_data,
                                                                            destination_user_data=destination_user_share, k_i=k_i, transaction_id=transaction_id)
            
            StepTwo_Mta_And_MtaWc.create_and_send_Ki_mta_wc_commitment(sending_user_public_share=sending_user_public_share,
                                                                               curve=curve, user_secret_data=user_secret_data,
                                                                                destination_user_data=destination_user_share, k_i=k_i, transaction_id=transaction_id)

    

    
    @staticmethod
    def create_and_send_Ki_mta_commitment(sending_user_public_share : user_public_share, curve : Curve,
                                           user_secret_data : user_secret_signature_share, destination_user_data : user_public_share,
                                             k_i :int, transaction_id : str):
        destination_user_public_share = user_public_share.from_dict(destination_user_data.user_public_keys_data)
        destination_user_public_key = PointJacobi() #RON TODO : deserialize the destinatoin user public key
        mta_protocol = MTAProtocolWithZKP(alice_public_share=sending_user_public_share, bob_public_share=destination_user_public_share, curve=curve,
                                              bob_public_g_power_secret=destination_user_public_key, b_value=None,
                                                alice_paillier_private_key=user_secret_data.paillier_secret_key)
            
            
        mta_enc_ki, mta_commitment_of_ki = mta_protocol.alice_encrypting_a_and_sending_commitment(a=k_i, alice_paillier_public_key=user_secret_data.paillier_public_key)
        insertion_success = db_dal.insert_alice_a_and_enc_a(transaction_id=transaction_id, user_index=sending_user_public_share.user_index,
                                                             counterparty_index=destination_user_data.user_index, a=k_i, enc_a=mta_enc_ki)
        if not insertion_success:
            print(f'Failed Recording encryption of k_i for target user : {destination_user_data.user_id}')
            raise SystemError(f'Failed Recording encryption of k_i for target user : {destination_user_data.user_id}')

        mta_commitment_message = MessageDTO(type=MessageType.MtaCommitmentAlice, data=mta_commitment_of_ki).model_dump_json()
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=destination_user_public_share.user_id, message=mta_commitment_message)
        return db_dal.update_alice_commitment(transaction_id=transaction_id, user_index=user_public_share.user_index, commitment_of_a=mta_commitment_message)

    @staticmethod
    def create_and_send_Ki_mta_wc_commitment(sending_user_public_share : user_public_share, curve : Curve,
                                           user_secret_data : user_secret_signature_share, destination_user_data : user_public_share,
                                             k_i :int, transaction_id : str):
        destination_user_public_share = user_public_share.from_dict(destination_user_data.user_public_keys_data)
        destination_user_public_key = PointJacobi() #RON TODO : deserialize the destinatoin user public key
        mta_wc_protocol = MtaWcProtocolWithZKP(alice_public_share=sending_user_public_share, bob_public_share=destination_user_public_share, curve=curve,
                                              bob_public_g_power_secret=destination_user_public_key, b_value=None,
                                                alice_paillier_private_key=user_secret_data.paillier_secret_key)
            
        
        mta_enc_ki, mta_wc_commitment_of_ki = mta_wc_protocol.alice_encrypting_a_and_sending_commitment(a=k_i, alice_paillier_public_key=user_secret_data.paillier_public_key)
        mta_commitment_message = MessageDTO(type=MessageType.MtaWcCommitmentAlice, data=mta_wc_commitment_of_ki).model_dump_json()
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=destination_user_public_share.user_id, message=mta_commitment_message)
        #RON TODO : Recored the commitment message

    def send_alice_mta_proof_for_challenge(wallet_id : str, transaction_id : str, user_index : int, destination_user_index : int):
        alice_mta_user_data = db_dal.get_mta_as_alice_user_data(transaction_id=transaction_id, user_index=user_index, counterparty_index=destination_user_index)
        #Should store in that stage : a, enc_a, alice_commitment and bob's challenge
        protocol, bob_user_matrix_id = StepTwo_Mta_And_MtaWc.get_mta_protocol(wallet_id=wallet_id, destination_user_index=destination_user_index)
        protocol : MTAProtocolWithZKP
        alice_proof_for_challenge = protocol.alice_sends_proof_answering_challenge(commitment_of_a=alice_mta_user_data.commitment_of_a, a=alice_mta_user_data.a,
                                                                                     verifier_challenge=alice_mta_user_data.bobs_challenge)
        alice_proof_for_challenge_message = MessageDTO(type=MessageType.MtaProofForChallengeAlice, data=alice_proof_for_challenge).model_dump_json()
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=bob_user_matrix_id, message=alice_proof_for_challenge_message)

    @staticmethod
    def get_mta_protocol(wallet_id : str, destination_user_index : int):
        wallet = db_dal.get_wallet_by_id(wallet_id=wallet_id)
        destination_user_wallet_user_data = db_dal.get_specific_wallet_user_data(wallet_id=wallet.wallet_id, traget_user_index_in_wallet=destination_user_index)
        bob_user_share = user_public_share.from_dict(destination_user_wallet_user_data.user_public_keys_data)
        bob_public_key_g_x =  GPowerX.from_dict(destination_user_wallet_user_data.g_power_x) # RON TODO : Fix that class
        alice_user_share = user_public_share.from_dict(db_dal.get_my_wallet_user_data(wallet_id=wallet.wallet_id).user_public_keys_data)
        curve = curve_by_name(wallet.curve_name)
        alice_secret_data = wallet.get_room_secret_user_data()
        return MTAProtocolWithZKP(alice_public_share=alice_user_share, bob_public_share=bob_user_share, curve=curve,
                                              bob_public_g_power_secret=bob_public_key_g_x, b_value=None,
                                                alice_paillier_private_key=alice_secret_data.paillier_secret_key), destination_user_wallet_user_data.user_matrix_id
    
    def alice_record_bob_encrypted_value_and_commitment_sending_challenge(wallet_id : str, transaction_id : str, user_index : int,
                                                                         destination_user_index : int, bob_encrypted_value : EncryptedNumber,
                                                                         bobs_commitment : Bob_ZKProof_ProverCommitment):
      
      insertion_success = db_dal.update_bobs_encrypted_value_and_commitment(transaction_id=transaction_id, user_index=user_index, bobs_encrypted_value=bob_encrypted_value,
                                                                            bobs_commitment=bobs_commitment)
      
      protocol, bob_user_matrix_id =  StepTwo_Mta_And_MtaWc.get_mta_protocol(wallet_id=wallet_id, destination_user_index=destination_user_index)                                                                      bobs_encrypted_value=bob_encrypted_value, bobs_commitment=bobs_commitment)
      if not insertion_success:
          print(f'Failed Recording encryption of bobs value for target user : {bob_user_matrix_id}')
          raise SystemError(f'Failed Recording encryption of k_i for target user : {bob_user_matrix_id}')
      alice_challenge = protocol.alice_challenging_bob_commitment()
      alice_challenge_message = MessageDTO(type=MessageType.MtaChallenge, data=alice_challenge).model_dump_json()
      MatrixService.instance().send_private_message_to_user(target_user_matrix_id=bob_user_matrix_id, message=alice_challenge_message)
      insertion_success = db_dal.update_alice_challenge(transaction_id=transaction_id, user_index=user_index, alice_challenge=alice_challenge)
      return insertion_success


    def alice_handles_bob_proof_for_challenge_and_finalize(bob_proof_for_challenge : Bob_ZKProof_Proof_For_Challenge, transaction_id : str, wallet_id : str, 
                                                           user_index : int, target_user_index : int):
        
        protocol, _ =  StepTwo_Mta_And_MtaWc.get_mta_protocol(wallet_id=wallet_id, destination_user_index=target_user_index)                                                                      bobs_encrypted_value=bob_encrypted_value, bobs_commitment=bobs_commitment)
        alice_secret = db_dal.get_wallet_by_id(wallet_id=wallet_id).get_room_secret_user_data()
        alice_mta_user_data = db_dal.get_mta_as_alice_user_data(transaction_id=transaction_id, user_index=user_index, counterparty_index=target_user_index)
        alice_additive_share = protocol.alice_finalize(proof_for_challenge=bob_proof_for_challenge, commitment=alice_mta_user_data.bobs_commitment, 
                                                       enc_result=alice_mta_user_data.bobs_encrypted_value, enc_a=alice_mta_user_data.enc_a, settings=protocol.Bob_Alg_verifier_Settings,
                                                       challenge=alice_mta_user_data.alice_challenge, alice_paillier_secret_key=alice_secret.paillier_secret_key)
        target_user_transaction_data = db_dal.get_transaction_user_data_by_index(transaction_id=transaction_id, user_index=target_user_index)
        target_user_transaction_data.add_mta_result(result_value=alice_additive_share, role='bob', protocol_type='mta')
        db_dal.update_transaction_user_data(transaction_user_data= target_user_transaction_data)

