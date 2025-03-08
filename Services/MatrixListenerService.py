from matrix_client.client import MatrixClient
from models.DTOs.message_dto import MessageDTO
from pydantic import ValidationError
from models.DTOs.transaction_dto import TransactionDTO
from models.models import user_public_share, wallet_key_generation_share, GPowerX
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.DTOs.MessageType import MessageType
import Services.TransactionService as TransactionService
import Services.UserShareService as UserShareService
import Services.WalletService as WalletService
from APIs.Algorithm_Steps_Implementation import StepTwoMtaAndMtaWcAliceOperations
from APIs.Algorithm_Steps_Implementation.StepTwoMtaAndMtaWcBobOperations import StepTwoMtaBobOperations
from phe import EncryptedNumber
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_Proof_For_Challenge, Bob_ZKProof_ProverCommitment
import time
from common_utils import deserialize_encrypted_number
from local_db.sql_db_dal import get_specific_wallet_user_data

class MatrixRoomListener:
    """
    Listens to messages in all rooms the user participates in and handles new invitations.
    This includes handling all MTA protocol messages for threshold ECDSA wallet operations.
    Updated to use the enhanced MessageDTO with metadata fields.
    """

    def __init__(self, client: MatrixClient):
        self.client = client
        self.client.add_listener(self._handle_event)  # Register global event listener
        self.running = False

    def listen_for_seconds(self, seconds: int):
        print(f"Listening for {seconds} seconds")
        self.start_listener()
        time.sleep(seconds)
        print("Stopping listen")
        self.stop_listener()
    
    def stop_listener(self):
        self.running = False
        self.client.stop_listener_thread()
        print("MatrixRoomListener stopped.")

    def start_listener(self):
        """ Starts the listener using `listen_forever` to handle incoming messages and room invitations. """
        self.running = True
        # stop the listener after listen_timeout_ms
        print("MatrixRoomListener started and listening for messages...")
        try:    
            self.client.start_listener_thread(timeout_ms=5000, exception_handler=self._handle_error)
        except Exception as e:
            print(f"Listener encountered an error: {e}")

    def _handle_event(self, event: dict):
        """
        Handles incoming messages and room invitations.
        - If it's a new room invitation, joins the room automatically.
        - If it's a message in an existing room, forwards it to the message handler.
        """
        event_type = event.get("type")

        if event_type == "m.room.message" and event["sender"] != self.client.user_id:
            room_id = event["room_id"]
            print(f"New message in room {room_id}: {event['content']['body']}")
            self._handle_room_message(room_id, event)

    def _handle_room_message(self, room_id: str, event: dict):
        """ Handles messages from existing rooms. """
        
        event_data = event["content"]["body"]
        try:
            message_obj = MessageDTO.model_validate_json(event_data)
            
            # Set metadata fields if they're not already provided in the message
            if not message_obj.sender_id:
                message_obj.sender_id = event["sender"]
            
            if not message_obj.wallet_id:
                message_obj.wallet_id = room_id
                
            # Now handle the message with all metadata available
            self._handle_message_DTO(message_obj, room_id)
            
        except (ValueError, KeyError, ValidationError) as e:
            print(f"Failed to validate message {event['content']['body']}")
            print(f"Error: {e}")
            return

    def _handle_error(self, exception: Exception):
        """ Handles exceptions that occur during event listening. """
        print(f"Listener error: {exception}")

    def _handle_message_DTO(self, message_dto: MessageDTO, wallet_id: str):
        """ 
        Handles a message DTO based on its message type.
        Includes handlers for all MTA protocol message types.
        Now uses the metadata fields from the enhanced MessageDTO.
        """
        try:
            # For backward compatibility, ensure wallet_id is set
            if not message_dto.wallet_id:
                message_dto.wallet_id = wallet_id
            
            wallet_id = message_dto.wallet_id or wallet_id
            transaction_id = message_dto.transaction_id if message_dto.transaction_id is not None else None
            
            # Get sender user index from metadata
            sender_index = message_dto.user_index
            sender_id = message_dto.sender_id
            
            # Wallet and Transaction Management
            if message_dto.type == MessageType.TransactionRequest:
                print(f"Transaction request received")
                transaction_request_obj: TransactionDTO = message_dto.data
                TransactionService.handler_new_transaction(transaction_request_obj)
                return
            
            elif message_dto.type == MessageType.TransactionResponse:
                print(f"Transaction response received")
                transaction_response_obj: TransactionResponseDTO = message_dto.data
                return TransactionService.handle_incoming_transaction_response(transaction_response_obj)
        
            elif message_dto.type == MessageType.UserPublicShare:
                print(f"User public share received")
                user_public_share_obj: user_public_share = message_dto.data
                return UserShareService.handle_incoming_public_share(user_public_share_obj, wallet_id)
            
            elif message_dto.type == MessageType.KeyGenerationShare:
                key_generation_share_obj: wallet_key_generation_share = message_dto.data
                print(f"Key generation share received")
                return UserShareService.handle_incoming_key_generation_share(key_generation_share_obj)
                
            elif message_dto.type == MessageType.Commitment:
                commitment_obj = message_dto.data
                print(f"Commitment received")
                # RON TODO : Handle commitment logic - required for Steps 3-5

            elif message_dto.type == MessageType.GPowerX:
                g_power_x_obj: GPowerX = message_dto.data
                print(f"GPowerX received from {g_power_x_obj.user_matrix_id}")
                return WalletService.save_incoming_g_power_x_to_db(g_power_x_obj)

            # Value Knowledge ZK Proof Handling
            elif message_dto.type == MessageType.ValueKnowledgeZkProof:
                print(f"Value knowledge ZK proof received")
                value_knowledge_zk_proof_obj = message_dto.data
                # Handle value knowledge ZK proof

            # MTA Protocol - Alice sends to Bob
            elif message_dto.type == MessageType.MtaAliceCommitment:
                print(f"MTA commitment from Alice received")
                mta_commitment_alice_obj = message_dto.data
                alice_paillier_pub_key = get_user_paillier_public_key(wallet_id, sender_id)
                StepTwoMtaBobOperations.process_alice_mta_commitment(
                    transaction_id=transaction_id,
                    user_index=self.client.user_id,
                    alice_index=sender_id,
                    enc_a=deserialize_encrypted_number(mta_commitment_alice_obj["enc_a"], alice_paillier_pub_key),
                    commitment_of_a=AliceZKProof_Commitment.from_dict(mta_commitment_alice_obj["commitment_of_a"]),
                    wallet_id=wallet_id
                )

            elif message_dto.type == MessageType.MtaAliceProofForChallenge:
                print(f"MTA proof for challenge from Alice received")
                alice_proof_obj = message_dto.data
                alice_proof = AliceZKProof_Proof_For_Challenge(
                    s=alice_proof_obj["s"],
                    s1=alice_proof_obj["s1"],
                    s2=alice_proof_obj["s2"]
                )
                
                StepTwoMtaBobOperations.verify_alice_proof_and_encrypt_value(
                    transaction_id=transaction_id,
                    user_index=self.client.user_id,
                    alice_index=sender_id,
                    alice_proof=alice_proof,
                    wallet_id=wallet_id
                )

            elif message_dto.type == MessageType.MtaAliceChallengeToBob:
                print(f"MTA challenge received from Alice")
                mta_challenge_obj = message_dto.data
                
                StepTwoMtaBobOperations.process_alice_challenge_and_send_proof(
                    transaction_id=transaction_id,
                    user_index=self.client.user_id,
                    alice_index=sender_id,
                    alice_challenge=mta_challenge_obj["challenge"],
                    wallet_id=wallet_id
                )

            # MTA Protocol - Bob sends to Alice
            elif message_dto.type == MessageType.MtaBobChallengeToAlice:
                print(f"MTA challenge received from Bob")
                bob_challenge_obj = message_dto.data
                
                # Alice answers Bob's challenge with a proof
                StepTwoMtaAndMtaWcAliceOperations.alice_answer_bob_challenge(
                    wallet_id=wallet_id,
                    transaction_id=transaction_id,
                    user_index=self.client.user_id,
                    destination_user_index=sender_id,
                    bob_challenge=bob_challenge_obj["challenge"]
                )

            elif message_dto.type == MessageType.MtaBobCommitment:
                print(f"MTA commitment from Bob received")
                mta_commitment_bob_obj = message_dto.data
                
                # Get Bob's public key for deserializing
                bob_paillier_pub_key = get_user_paillier_public_key(wallet_id, sender_id)
                
                # Alice records Bob's commitment and responds with challenge
                StepTwoMtaAndMtaWcAliceOperations.alice_record_bob_encrypted_value_and_commitment_sending_challenge(
                    wallet_id=wallet_id,
                    transaction_id=transaction_id,
                    user_index=self.client.user_id,
                    destination_user_index=sender_id,
                    bob_encrypted_value=deserialize_encrypted_number(mta_commitment_bob_obj["enc_result"], bob_paillier_pub_key),
                    bobs_commitment=Bob_ZKProof_ProverCommitment.from_dict(mta_commitment_bob_obj["commitment"])
                )

            elif message_dto.type == MessageType.MtaBobProofForChallenge:
                print(f"MTA proof for challenge from Bob received")
                bob_proof_obj = message_dto.data
                
                # Convert to Bob proof object
                bob_proof = Bob_ZKProof_Proof_For_Challenge(
                    s=bob_proof_obj["s"],
                    s1=bob_proof_obj["s1"],
                    s2=bob_proof_obj["s2"],
                    t1=bob_proof_obj["t1"],
                    t2=bob_proof_obj["t2"]
                )
                
                # Alice handles Bob's proof and finalizes MTA
                StepTwoMtaAndMtaWcAliceOperations.alice_handles_bob_proof_for_challenge_and_finalize(
                    bob_proof_for_challenge=bob_proof,
                    transaction_id=transaction_id,
                    wallet_id=wallet_id,
                    user_index=self.client.user_id,
                    target_user_index=sender_id
                )

            # MTA WC Protocol (with check - for secret key) - Similar pattern for other message types
            # ...

            else:
                print(f"Unknown message type: {message_dto.type}")
                return
                
        except ValidationError as e:
            print(f"Validation error: {e}")
            return
        except Exception as e:
            print(f"Error handling message: {e}")
            return


# Helper function to get a user's Paillier public key
def get_user_paillier_public_key(wallet_id, user_matrix_id):
    """Get a user's Paillier public key from the wallet user data"""
    user_data = get_specific_wallet_user_data(wallet_id, user_matrix_id)
    if not user_data:
        raise ValueError(f"No user data found for wallet {wallet_id} and user {user_matrix_id}")
    
    user_share = user_public_share.from_dict(user_data.user_public_keys_data)
    return user_share.paillier_public_key