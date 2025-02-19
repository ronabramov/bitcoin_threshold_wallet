from matrix_client.client import MatrixClient
from matrix_client.room import Room
import time
from models.DTOs.message_dto import MessageDTO
from pydantic import ValidationError
from models.DTOs.transaction_dto import TransactionDTO
from models.models import WalletGenerationMessage, user_public_share, key_generation_share
from models.transaction_response import TransactionResponse
from models.DTOs.message_dto import MessageType
from models.commitment import Commitment
from models.value_knowledge_zk_proof import value_knowledge_zk_proof
from models.protocols.MtaAndMtaWcMessages import MtaChallenge, MtaCommitmentAlice, MtaCommitmentBob, MtaProofForChallengeAlice, MtaProofForChallengeBob, MtaWcCommitmentBob
from local_db import sql_db_dal
from Services.TransactionService import TransactionService


class MatrixRoomListener:
    """
    Listens to messages in all rooms the user participates in and handles new invitations.
    """

    def __init__(self, client: MatrixClient):
        self.client = client
        self.client.add_listener(self._handle_event)  # Register global event listener
        self.running = False

    def start_listener(self):
        """ Starts the listener using `listen_forever` to handle incoming messages and room invitations. """
        self.running = True
        print("MatrixRoomListener started and listening for messages...")

        try:
            self.client.listen_forever(timeout_ms=30000, exception_handler=self._handle_error)
        except Exception as e:
            print(f"Listener encountered an error: {e}")

    def _handle_event(self, event: dict):
        """
        Handles incoming messages and room invitations.
        - If it's a new room invitation, joins the room automatically.
        - If it's a message in an existing room, forwards it to the message handler.
        """
        event_type = event.get("type")

        if event_type == "m.room.message":
            room_id = event["room_id"]
            print(f"New message in room {room_id}: {event['content']['body']}")
            self._handle_room_message(room_id, event)

        elif event_type == "m.room.member" and event.get("content", {}).get("membership") == "invite":
            room_id = event["room_id"]
            print(f"New room invitation detected: {room_id}")
            self._handle_room_invitation(room_id)

    def _handle_room_message(self, room_id: str, event: dict):
        """ Handles messages from existing rooms (to be implemented later). """
        
        event_data = event["content"]["body"]
        try:
            message_obj = MessageDTO.model_validate_json(event_data)
        except (ValueError, KeyError, ValidationError):
            print(f"Failed to validate message {event['content']['body']}")
            pass 
        self._handle_message_DTO(message_obj)
        # Forward to a message handler (to be implemented later)
        print(f"Message received in room {room_id}: {event['content']['body']}")

    def _handle_room_invitation(self, room_id: str):
        """ Handles new room invitations and joins automatically. """
        try:
            joined_room = self.client.join_room(room_id)
            print(f"Successfully joined room {joined_room.room_id}")
        except Exception as e:
            print(f"Failed to join room {room_id}: {e}")

    def _handle_error(self, exception: Exception):
        """ Handles exceptions that occur during event listening. """
        print(f"Listener error: {exception}")

    def stop_listener(self):
        """ Stops the listener gracefully. """
        self.running = False
        self.client.stop_listener_thread()
        print("MatrixRoomListener stopped.")

    def _handle_message_DTO(self, message_dto: MessageDTO):
        """ Handles a message DTO. """
        print(f"Message received: {message_dto}")
        try:
            if message_dto.type == MessageType.TransactionRequest:
                transaction_request_obj = TransactionDTO.model_validate_json(message_dto.data)
                sql_db_dal.insert_new_transaction(transaction_request_obj)
                # user need to fetch the transaction from local db and display it in the UI
                return
                print(f"Transaction request received: {transaction_request_obj}")
            
            elif message_dto.type == MessageType.TransactionResponse:
                transaction_response_obj = TransactionResponse.model_validate_json(message_dto.data)
                return TransactionService.handle_incoming_transaction(transaction_response_obj)
        
            elif message_dto.type == MessageType.UserPublicShare:
                user_public_share_obj = user_public_share.model_validate_json(message_dto.data)
                print(f"User public share received: {user_public_share_obj}")
            
            elif message_dto.type == MessageType.KeyGenerationShare:
                key_generation_share_obj = key_generation_share.model_validate_json(message_dto.data)
                print(f"Key generation share received: {key_generation_share_obj}")
            
            elif message_dto.type == MessageType.WalletGenerationMessage:
                wallet_generation_message_obj = WalletGenerationMessage.model_validate_json(message_dto.data)
                print(f"Wallet generation message received: {wallet_generation_message_obj}")
            
            elif message_dto.type == MessageType.Commitment:
                commitment_obj = Commitment.model_validate_json(message_dto.data)
                print(f"Commitment received: {commitment_obj}")
            
            elif message_dto.type == MessageType.ValueKnowledgeZkProof:
                value_knowledge_zk_proof_obj = value_knowledge_zk_proof.model_validate_json(message_dto.data)
                print(f"Value knowledge ZK proof received: {value_knowledge_zk_proof_obj}")
            
            elif message_dto.type == MessageType.MtaChallenge:
                mta_challenge_obj = MtaChallenge.model_validate_json(message_dto.data)
                print(f"MTA challenge received: {mta_challenge_obj}")
            
            elif message_dto.type == MessageType.MtaCommitmentAlice:
                mta_commitment_alice_obj = MtaCommitmentAlice.model_validate_json(message_dto.data)
                print(f"MTA commitment Alice received: {mta_commitment_alice_obj}")
            
            elif message_dto.type == MessageType.MtaCommitmentBob:
                mta_commitment_bob_obj = MtaCommitmentBob.model_validate_json(message_dto.data)
                print(f"MTA commitment Bob received: {mta_commitment_bob_obj}")
            
            elif message_dto.type == MessageType.MtaProofForChallengeAlice:
                mta_proof_for_challenge_alice_obj = MtaProofForChallengeAlice.model_validate_json(message_dto.data)
                print(f"MTA proof for challenge Alice received: {mta_proof_for_challenge_alice_obj}")
            
            elif message_dto.type == MessageType.MtaProofForChallengeBob:
                mta_proof_for_challenge_bob_obj = MtaProofForChallengeBob.model_validate_json(message_dto.data)
                print(f"MTA proof for challenge Bob received: {mta_proof_for_challenge_bob_obj}")
            elif message_dto.type == MessageType.MtaWcCommitmentBob:
                mta_wc_commitment_bob_obj = MtaWcCommitmentBob.model_validate_json(message_dto.data)
                print(f"MTA WC commitment Bob received: {mta_wc_commitment_bob_obj}")
            else:
                print(f"Unknown message type: {message_dto.type}")
                return
            
        except ValidationError as e:
            print(f"Validation error: {e}")
            return
            