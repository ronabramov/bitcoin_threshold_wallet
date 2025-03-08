from matrix_client.client import MatrixClient
from models.DTOs.message_dto import MessageDTO
from pydantic import ValidationError
from models.DTOs.transaction_dto import TransactionDTO
from models.models import user_public_share, wallet_key_generation_share
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.DTOs.MessageType import MessageType
import Services.TransactionService as TransactionService
import Services.UserShareService as UserShareService
from APIs.Algorithm_Steps_Implementation import StepTwoMtaAndMtaWcAliceOperations
from APIs.Algorithm_Steps_Implementation.StepTwoMtaAndMtaWcBobOperations import StepTwoMtaBobOperations
from phe import EncryptedNumber
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_Proof_For_Challenge, Bob_ZKProof_ProverCommitment, Bob_ZKProof_RegMta_Prover_Settings, Bob_ZKProof_RegMta_Settings
import time
from Services.WalletService import save_incoming_g_power_x_to_db
from models.models import GPowerX

class MatrixRoomListener:
    """
    Listens to messages in all rooms the user participates in and handles new invitations.
    """

    def __init__(self, client: MatrixClient):
        self.client = client
        self.client.add_listener(self._handle_event)  # Register global event listener
        self.running = False

    def listen_for_seconds(self, seconds : int):
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
        """ Handles messages from existing rooms (to be implemented later). """
        
        event_data = event["content"]["body"]
        try:
            message_obj = MessageDTO.model_validate_json(event_data)
        except (ValueError, KeyError, ValidationError) as e:
            print(f"Failed to validate message {event['content']['body']}")
            print(f"Error: {e}")
            return
        self._handle_message_DTO(message_obj, room_id)

    def _handle_error(self, exception: Exception):
        """ Handles exceptions that occur during event listening. """
        print(f"Listener error: {exception}")

    def stop_listener(self):
        """ Stops the listener gracefully. """
        self.running = False
        self.client.stop_listener_thread()
        print("MatrixRoomListener stopped.")

    def _handle_message_DTO(self, message_dto: MessageDTO, wallet_id: str):
        """ Handles a message DTO. """
        try:
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

            # this is not needed - we already handle this in the RoomManagementAPI (RON right?ß)
            # elif message_dto.type == MessageType.WalletGenerationMessage:
            #     wallet_generation_message_obj = message_dto.data
            #     print(f"Wallet generation message received: {wallet_generation_message_obj}")
                # here
            
            elif message_dto.type == MessageType.ValueKnowledgeZkProof:
                value_knowledge_zk_proof_obj = message_dto.data
                print(f"Value knowledge ZK proof received")
            
            elif message_dto.type == MessageType.MtaCommitmentAlice:
                print(f"MTA commitment from Alice received")
                mta_commitment_alice_obj = message_dto.data

                StepTwoMtaBobOperations.process_alice_mta_commitment(
                    transaction_id=wallet_id,
                    user_index=self.client.user_id,
                    alice_index=mta_commitment_alice_obj["user_index"],
                    enc_a=EncryptedNumber.from_dict(mta_commitment_alice_obj["enc_a"]),
                    commitment_of_a=AliceZKProof_Commitment.from_dict(mta_commitment_alice_obj["commitment_of_a"]),
                    wallet_id=wallet_id
                )

            elif message_dto.type == MessageType.MtaProofForChallengeAlice:
                print(f"MTA proof for challenge from Alice received")
                proof_obj = Bob_ZKProof_Proof_For_Challenge.from_dict(message_dto.data)
                
                StepTwoMtaBobOperations.verify_alice_proof_and_encrypt_value(
                    transaction_id=wallet_id,
                    user_index=self.client.user_id,
                    alice_index=proof_obj.user_index,
                    alice_proof=proof_obj,
                    wallet_id=wallet_id
                )

            elif message_dto.type == MessageType.MtaChallenge:
                print(f"MTA challenge received from Alice")
                mta_challenge_obj = message_dto.data
                
                StepTwoMtaBobOperations.process_alice_challenge_and_send_proof(
                    transaction_id=wallet_id,
                    user_index=self.client.user_id,
                    alice_index=mta_challenge_obj["user_index"],
                    alice_challenge=mta_challenge_obj["challenge"],
                    wallet_id=wallet_id
                )

            # MtA Protocol Handling - Bob
            elif message_dto.type == MessageType.MtaCommitmentBob:
                print(f"MTA commitment from Bob received")
                mta_commitment_bob_obj = message_dto.data
                
                StepTwoMtaAndMtaWcAliceOperations.alice_record_bob_encrypted_value_and_commitment_sending_challenge(
                    wallet_id=wallet_id,
                    transaction_id=wallet_id,
                    user_index=self.client.user_id,
                    destination_user_index=mta_commitment_bob_obj["user_index"],
                    bob_encrypted_value=EncryptedNumber.from_dict(mta_commitment_bob_obj["enc_result"]),
                    bobs_commitment=Bob_ZKProof_ProverCommitment.from_dict(mta_commitment_bob_obj["commitment"])
                )

            elif message_dto.type == MessageType.MtaProofForChallengeBob:
                print(f"MTA proof for challenge from Bob received")
                proof_obj = Bob_ZKProof_Proof_For_Challenge.from_dict(message_dto.data)
                
                StepTwoMtaAndMtaWcAliceOperations.alice_handles_bob_proof_for_challenge_and_finalize(
                    bob_proof_for_challenge=proof_obj,
                    transaction_id=wallet_id,
                    wallet_id=wallet_id,
                    user_index=self.client.user_id,
                    target_user_index=proof_obj.user_index
                )

            # MtA WC Protocol Handling
            elif message_dto.type == MessageType.MtaWcCommitmentBob:
                print(f"MTA WC commitment from Bob received")
                mta_wc_commitment_bob_obj = message_dto.data
                
                # TODO: Implement MtA WC Processing

            # Value Knowledge ZK Proof Handling
            elif message_dto.type == MessageType.ValueKnowledgeZkProof:
                print(f"Value knowledge ZK proof received")
                value_knowledge_zk_proof_obj = message_dto.data
                
                # TODO: Implement Value Knowledge ZK Proof Handling

            # GPowerX Handling
            # elif message_dto.type == MessageType.GPowerX:
            #     g_power_x_obj: GPowerX = message_dto.data
            #     print(f"GPowerX received from {g_power_x_obj.user_matrix_id}")
            #     return WalletService.save_incoming_g_power_x_to_db(g_power_x_obj)

            else:
                print(f"Unknown message type: {message_dto.type}")
                return
                
        except ValidationError as e:
            print(f"Validation error: {e}")
            return
                