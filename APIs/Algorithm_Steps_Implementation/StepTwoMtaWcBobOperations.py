from local_db.sql_db import Wallet
import local_db.sql_db_dal as db_dal
from models.models import user_public_share, GPowerX
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from ecdsa.curves import curve_by_name
from models.DTOs.MessageType import MessageType
from models.DTOs.message_dto import MessageDTO
from Services.MatrixService import MatrixService
from phe import EncryptedNumber
from models.protocols.MtaWc_protocl import MtaWcProtocolWithZKP
from Services.Context import Context


class StepTwoMtaWcBobOperations:

    def process_alice_mtawc_commitment(self, transaction_id: str, user_index: int, alice_index: int, 
                                     enc_a: EncryptedNumber, commitment_of_a: AliceZKProof_Commitment, wallet_id: str):
        """
        Bob processes Alice's encrypted value and commitment for MtaWc protocol.
        He verifies the commitment and sends a challenge.
        """
        db_dal.insert_mtawc_as_bob(transaction_id, user_index, alice_index, enc_a, commitment_of_a)
        protocol, alice_matrix_id = StepTwoMtaWcBobOperations.get_mtawc_protocol(wallet_id, alice_index)
        bobs_challenge = protocol.bob_challenging_a_commitment()
        challenge_message = MessageDTO(type=MessageType.MtaWcChallenge, data=bobs_challenge, sender_id=Context.matrix_user_id,
                                        wallet_id=wallet_id, transaction_id=transaction_id, user_index=user_index).model_dump_json()
        
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=alice_matrix_id, message=challenge_message)
        db_dal.update_mtawc_bobs_challenge_as_bob(transaction_id, user_index, bobs_challenge)


    def verify_alice_proof_and_encrypt_value_with_check(self, transaction_id: str, user_index: int, alice_index: int, 
                                             alice_proof: AliceZKProof_Proof_For_Challenge, wallet_id: str):
        """
        Bob verifies Alice's proof for MtaWc. If valid, he encrypts `(a^b + β')`, 
        creates a commitment, and sends them to Alice.
        """
        user_pub_key = user_public_share.from_dict(db_dal.get_my_wallet_user_data(wallet_id=wallet_id).user_public_keys_data).paillier_public_key
        destination_user_wallet_user_data = db_dal.get_specific_wallet_user_data(wallet_id=wallet_id, traget_user_index_in_wallet= alice_index)
        destination_user_pub_key = user_public_share.from_dict(destination_user_wallet_user_data.user_public_keys_data)
        bob_mtawc_data = db_dal.get_mtawc_as_bob(transaction_id = transaction_id, user_index = user_index, user_paillier_pub_key=user_pub_key,
                                              counterparty_index= alice_index, counter_party_paillier_pub_key= destination_user_pub_key)
        protocol, alice_matrix_id = StepTwoMtaWcBobOperations.get_mtawc_protocol(wallet_id, alice_index)
        enc_result, beta_prime, bobs_commitment = protocol.bob_verify_a_commiting_encrypting_b(
            b=bob_mtawc_data.b, enc_a=bob_mtawc_data.enc_a, challenge=bob_mtawc_data.bobs_challenge, 
            proof_of_a=alice_proof, commitment_of_a=bob_mtawc_data.commitment_of_a, 
            prover_settings=protocol.bob_alg_prover_settings
        )
        db_dal.update_mtawc_bobs_encrypted_value_and_commitment_as_bob(transaction_id, user_index, enc_result, bobs_commitment, beta_prime)

        enc_result_message = MessageDTO(type=MessageType.MtaWcEncValueBob, data={"enc_result": enc_result, "commitment": bobs_commitment},
                                        sender_id=Context.matrix_user_id(), wallet_id=wallet_id, 
                                        transaction_id=transaction_id, user_index=user_index).model_dump_json()
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=alice_matrix_id, message=enc_result_message)

    def process_alice_challenge_and_send_proof_with_check(self, transaction_id: str, user_index: int, alice_index: int, 
                                               alice_challenge: int, wallet_id: str):
        """
        Bob processes Alice's challenge and sends proof with the additional check for MtaWc.
        """
        protocol, alice_matrix_id = StepTwoMtaWcBobOperations.get_mtawc_protocol(wallet_id, alice_index)
        user_pub_key = user_public_share.from_dict(db_dal.get_my_wallet_user_data(wallet_id=wallet_id).user_public_keys_data).paillier_public_key
        destination_user_wallet_user_data = db_dal.get_specific_wallet_user_data(wallet_id=wallet_id, traget_user_index_in_wallet= alice_index)
        destination_user_pub_key = user_public_share.from_dict(destination_user_wallet_user_data.user_public_keys_data)
        bob_mtawc_data = db_dal.get_mtawc_as_bob(transaction_id = transaction_id, user_index = user_index, user_paillier_pub_key=user_pub_key,
                                              counterparty_index= alice_index, counter_party_paillier_pub_key= destination_user_pub_key)

        bob_proof = protocol.bob_provide_proof_for_alice_challenge(commitment_of_b_and_beta_prime=bob_mtawc_data.bobs_commitment,
                                                                    settings=protocol.bob_alg_prover_settings, challenge=alice_challenge)

        db_dal.update_mtawc_bob_proof_for_challenge_as_bob(transaction_id, user_index, bob_proof)
        proof_message = MessageDTO(type=MessageType.MtaWcProofForChallengeBob, data=bob_proof, sender_id=Context.matrix_user_id(),
                                    wallet_id=wallet_id, transaction_id=transaction_id, user_index=user_index).model_dump_json()
        
        MatrixService.instance().send_private_message_to_user(target_user_matrix_id=alice_matrix_id, message=proof_message)

    def finalize_mtawc_and_compute_beta(self, transaction_id: str, user_index: int, alice_index: int, wallet_id: str):
        """
        Bob finalizes the MtaWc protocol and computes his final additive share (β).
        """
        protocol, _ = StepTwoMtaWcBobOperations.get_mtawc_protocol(wallet_id, alice_index)
        user_pub_key = user_public_share.from_dict(db_dal.get_my_wallet_user_data(wallet_id=wallet_id).user_public_keys_data).paillier_public_key
        destination_user_wallet_user_data = db_dal.get_specific_wallet_user_data(wallet_id=wallet_id, traget_user_index_in_wallet= alice_index)
        destination_user_pub_key = user_public_share.from_dict(destination_user_wallet_user_data.user_public_keys_data)
        bob_mtawc_data = db_dal.get_mtawc_as_bob(transaction_id = transaction_id, user_index = user_index, user_paillier_pub_key=user_pub_key,
                                              counterparty_index= alice_index, counter_party_paillier_pub_key= destination_user_pub_key)
        
        beta = protocol.bob_finalize(beta_prime=bob_mtawc_data.beta_prime)
        transaction_user_data = db_dal.get_transaction_user_data_by_index(transaction_id, user_index)
        transaction_user_data.add_mta_result(result_value=beta, role='bob', protocol_type='mta_wc')
        db_dal.update_transaction_user_data(transaction_user_data)

    @staticmethod
    def get_mtawc_protocol(wallet_id: str, destination_user_index: int):
        """
        Gets the MtaWc protocol instance for the wallet and destination user.
        """
        wallet = db_dal.get_wallet_by_id(wallet_id)
        destination_user_wallet_user_data = db_dal.get_specific_wallet_user_data(wallet.wallet_id, destination_user_index)

        bob_user_share = user_public_share.from_dict(destination_user_wallet_user_data.user_public_keys_data)
        bob_public_key_g_x = GPowerX.from_dict(destination_user_wallet_user_data.g_power_x)

        bob_user_data = user_public_share.from_dict(db_dal.get_my_wallet_user_data(wallet.wallet_id).user_public_keys_data)
        curve = curve_by_name(wallet.curve_name)
        bob_secret_data = wallet.get_room_secret_user_data()

        return MtaWcProtocolWithZKP(alice_public_share=bob_user_share, bob_public_share=bob_user_data, curve=curve,
                                  bob_public_g_power_secret=bob_public_key_g_x, b_value=None, #RON TODO : Check why there is no b_value 
                                  alice_paillier_private_key=bob_secret_data.paillier_secret_key), destination_user_wallet_user_data.user_matrix_id