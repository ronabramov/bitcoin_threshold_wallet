import random
from local_db.db_dal import (
    get_wallet_by_id, get_specific_wallet_user_data, 
    get_all_wallet_user_data, get_transaction_by_id
)
from models.models import user_public_share
from protocols.mta_protocol import MTAProtocolWithZKP
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_Proof_For_Challenge, Bob_ZKProof_ProverCommitment, Bob_ZKProof_RegMta_Settings
from phe import EncryptedNumber
from ecdsa import curves, NIST256p
from ecdsa.ellipticcurve import PointJacobi
from APIs.MatrixCommunicationAPI import MatrixCommunicationAPI
from models.DTOs.MessageType import MessageType
from models.DTOs.message_dto import MessageDTO
from common_utils import serialize_encryped_number
from Services.Context import Context

class StepTwoMtaAndMtaWcAliceOperations:
    """
    Operations for the MTA protocol, where Alice initiates the protocol.
    Alice holds value 'a' and sends an encrypted commitment to Bob.
    """

    @staticmethod
    def initialize_mta_protocol_as_alice(wallet_id: str, transaction_id: str, target_user_index: str):
        """
        Alice initializes the MTA protocol with a target user (Bob).
        She encrypts her value 'a' and sends a commitment to Bob.
        """
        # Get wallet data
        wallet = get_wallet_by_id(wallet_id)
        if not wallet:
            print(f"No wallet found with ID {wallet_id}")
            return False
        
        # Get the transaction
        transaction = get_transaction_by_id(transaction_id)
        if not transaction:
            print(f"No transaction found with ID {transaction_id}")
            return False
        
        # Get Alice's data (current user)
        alice_data = get_specific_wallet_user_data(wallet_id, Context.matrix_user_id())
        if not alice_data:
            print(f"No user data found for user {Context.matrix_user_id()} in wallet {wallet_id}")
            return False
        
        alice_user_index = alice_data.user_index
        
        # Get Bob's data (target user)
        bob_data = get_specific_wallet_user_data(wallet_id, target_user_index)
        if not bob_data:
            print(f"No user data found for user {target_user_index} in wallet {wallet_id}")
            return False
        
        # Construct public shares
        alice_public_share = user_public_share.from_dict(alice_data.user_public_keys_data)
        bob_public_share = user_public_share.from_dict(bob_data.user_public_keys_data)
        
        # Set up the curve
        curve = NIST256p
        
        # Create MTA protocol instance
        mta_protocol = MTAProtocolWithZKP(
            alice_public_share=alice_public_share,
            bob_public_share=bob_public_share,
            curve=curve,
            bob_public_g_power_secret=None,  # Not needed for Alice
            alice_paillier_private_key=get_alice_paillier_private_key()  # Function to retrieve Alice's private key
        )
        
        # Alice generates a random 'a' value
        a = random.randint(1, curve.order - 1)
        
        # Alice encrypts 'a' and generates a commitment
        enc_a, commitment_of_a = mta_protocol.alice_encrypting_a_and_sending_commitment(
            a=a,
            alice_paillier_public_key=alice_public_share.paillier_public_key
        )
        
        # Store Alice's 'a', enc_a, and commitment in the database
        # This would insert into the appropriate DB table for MTA protocol data
        
        # Send Alice's encrypted 'a' and commitment to Bob
        matrix_api = MatrixCommunicationAPI()
        alice_commitment_message = {
            # Only include protocol-specific data, not metadata
            "enc_a": serialize_encryped_number(enc_a),
            "commitment_of_a": commitment_of_a.to_dict()
        }
        
        # Create message with metadata
        message_dto = MessageDTO(
            type=MessageType.MtaAliceCommitment, 
            data=alice_commitment_message,
            sender_id=Context.matrix_user_id(),
            wallet_id=wallet_id,
            transaction_id=transaction_id,
            user_index=alice_user_index
        )
        
        matrix_api.send_message_to_room(wallet_id, message_dto.model_dump_json())
        
        print(f"Sent MTA commitment to Bob (user {target_user_index})")
        return True

    @staticmethod
    def alice_answer_bob_challenge(
        wallet_id: str,
        transaction_id: str,
        user_index: str,
        destination_user_index: str,
        bob_challenge: int
    ):
        """
        Alice answers Bob's challenge with a proof.
        """
        # Get wallet and user data as in previous methods
        wallet = get_wallet_by_id(wallet_id)
        if not wallet:
            print(f"No wallet found with ID {wallet_id}")
            return False
        
        # Get Alice's data
        alice_data = get_specific_wallet_user_data(wallet_id, user_index)
        if not alice_data:
            print(f"No user data found for user {user_index} in wallet {wallet_id}")
            return False
        
        alice_user_index = alice_data.user_index
        
        # Get Bob's data
        bob_data = get_specific_wallet_user_data(wallet_id, destination_user_index)
        if not bob_data:
            print(f"No user data found for user {destination_user_index} in wallet {wallet_id}")
            return False
        
        # Construct public shares
        alice_public_share = user_public_share.from_dict(alice_data.user_public_keys_data)
        bob_public_share = user_public_share.from_dict(bob_data.user_public_keys_data)
        
        # Set up the curve
        curve = NIST256p
        
        # Initialize MTA protocol
        mta_protocol = MTAProtocolWithZKP(
            alice_public_share=alice_public_share,
            bob_public_share=bob_public_share,
            curve=curve,
            bob_public_g_power_secret=None,  # Not needed for Alice
            alice_paillier_private_key=get_alice_paillier_private_key()
        )
        
        # Retrieve Alice's 'a' and commitment from the database
        # For demonstration, we'll assume these values are available
        a = None  # Alice's secret value
        commitment_of_a = None  # Alice's commitment
        
        # Generate proof for Bob's challenge
        proof_for_challenge = mta_protocol.alice_sends_proof_answering_challenge(
            commitment_of_a=commitment_of_a,
            a=a,
            verifier_challenge=bob_challenge
        )
        
        # Store the proof in the database
        # This would update the appropriate DB table
        
        # Send the proof to Bob
        matrix_api = MatrixCommunicationAPI()
        
        # Create message with metadata
        message_dto = MessageDTO(
            type=MessageType.MtaAliceProofForChallenge, 
            data=proof_for_challenge.to_dict(),
            sender_id=Context.matrix_user_id(),
            wallet_id=wallet_id,
            transaction_id=transaction_id,
            user_index=alice_user_index
        )
        
        matrix_api.send_message_to_room(wallet_id, message_dto.model_dump_json())
        
        print(f"Sent MTA proof to Bob (user {destination_user_index})")
        return True

    @staticmethod
    def alice_record_bob_encrypted_value_and_commitment_sending_challenge(
        wallet_id: str,
        transaction_id: str,
        user_index: str,
        destination_user_index: str,
        bob_encrypted_value: EncryptedNumber,
        bobs_commitment: Bob_ZKProof_ProverCommitment
    ):
        """
        Alice records Bob's encrypted value and commitment,
        then sends a challenge to Bob.
        """
        # Get wallet and user data
        wallet = get_wallet_by_id(wallet_id)
        if not wallet:
            print(f"No wallet found with ID {wallet_id}")
            return False
        
        # Get Alice's data
        alice_data = get_specific_wallet_user_data(wallet_id, user_index)
        if not alice_data:
            print(f"No user data found for user {user_index} in wallet {wallet_id}")
            return False
        
        alice_user_index = alice_data.user_index
        
        # Get Bob's data
        bob_data = get_specific_wallet_user_data(wallet_id, destination_user_index)
        if not bob_data:
            print(f"No user data found for user {destination_user_index} in wallet {wallet_id}")
            return False
        
        # Store Bob's encrypted value and commitment in the database
        # This would update the appropriate DB table
        
        # Generate a challenge for Bob
        curve = NIST256p
        challenge = random.randint(1, curve.order - 1)
        
        # Store Alice's challenge in the database
        # This would update the appropriate DB table
        
        # Send the challenge to Bob
        matrix_api = MatrixCommunicationAPI()
        challenge_message = {
            "challenge": challenge
        }
        
        # Create message with metadata
        message_dto = MessageDTO(
            type=MessageType.MtaAliceChallengeToBob, 
            data=challenge_message,
            sender_id=Context.matrix_user_id(),
            wallet_id=wallet_id,
            transaction_id=transaction_id,
            user_index=alice_user_index
        )
        
        matrix_api.send_message_to_room(wallet_id, message_dto.model_dump_json())
        
        print(f"Sent MTA challenge to Bob (user {destination_user_index})")
        return True

    @staticmethod
    def alice_handles_bob_proof_for_challenge_and_finalize(
        bob_proof_for_challenge: Bob_ZKProof_Proof_For_Challenge,
        transaction_id: str,
        wallet_id: str,
        user_index: str,
        target_user_index: str
    ):
        """
        Alice verifies Bob's proof and finalizes the MTA protocol,
        obtaining her additive share of the product a*b.
        """
        # Get wallet and user data
        wallet = get_wallet_by_id(wallet_id)
        if not wallet:
            print(f"No wallet found with ID {wallet_id}")
            return False
        
        # Get Alice's data
        alice_data = get_specific_wallet_user_data(wallet_id, user_index)
        if not alice_data:
            print(f"No user data found for user {user_index} in wallet {wallet_id}")
            return False
        
        # Get Bob's data
        bob_data = get_specific_wallet_user_data(wallet_id, target_user_index)
        if not bob_data:
            print(f"No user data found for user {target_user_index} in wallet {wallet_id}")
            return False
        
        # Construct public shares
        alice_public_share = user_public_share.from_dict(alice_data.user_public_keys_data)
        bob_public_share = user_public_share.from_dict(bob_data.user_public_keys_data)
        
        # Set up the curve
        curve = NIST256p
        
        # Initialize MTA protocol
        mta_protocol = MTAProtocolWithZKP(
            alice_public_share=alice_public_share,
            bob_public_share=bob_public_share,
            curve=curve,
            bob_public_g_power_secret=None,  # Not needed for Alice
            alice_paillier_private_key=get_alice_paillier_private_key()
        )
        
        # Retrieve from the database:
        # - Bob's commitment
        # - Encrypted result from Bob
        # - Alice's encrypted 'a'
        # - Alice's challenge
        # For demonstration, we'll assume these values are available
        bob_commitment = None  # Bob's commitment
        enc_result = None  # Encrypted result from Bob
        enc_a = None  # Alice's encrypted 'a'
        challenge = None  # Alice's challenge
        
        # Create settings for verification
        bob_verifier_settings = Bob_ZKProof_RegMta_Settings(
            public_key=bob_public_share.paillier_public_key,
            verifier_modulus=alice_public_share.user_modulus,
            X=None,  # Not needed for standard MTA
            curve=curve
        )
        
        # Alice verifies Bob's proof and finalizes her share
        alpha = mta_protocol.alice_finalize(
            proof_for_challenge=bob_proof_for_challenge,
            commitment=bob_commitment,
            enc_result=enc_result,
            enc_a=enc_a,
            settings=bob_verifier_settings,
            challenge=challenge,
            alice_paillier_secret_key=get_alice_paillier_private_key()
        )
        
        # Store Alice's final result (alpha) in the transaction user data
        # This would update the appropriate field in the TransactionUserData table
        
        print(f"MTA protocol as Alice completed with Bob (user {target_user_index})")
        return True

    # Similar methods for MtaWc protocol would follow the same pattern
    # with appropriate message types

# Helper function to get Alice's Paillier private key
def get_alice_paillier_private_key():
    """
    Retrieves Alice's Paillier private key.
    In a real implementation, this would be securely stored and retrieved.
    """
    # This is a placeholder - in a real implementation, this would
    # retrieve the private key from secure storage
    return None  # Replace with actual implementation