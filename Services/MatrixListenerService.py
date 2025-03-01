from matrix_client.client import MatrixClient
from models.DTOs.message_dto import MessageDTO
from pydantic import ValidationError
from models.DTOs.transaction_dto import TransactionDTO
from models.models import user_public_share, wallet_key_generation_share
from models.DTOs.transaction_response_dto import TransactionResponseDTO
from models.DTOs.MessageType import MessageType
import Services.TransactionService as TransactionService
import Services.UserShareService as UserShareService

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

        if event_type == "m.room.message" and event["sender"] != self.client.user_id:
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
        except (ValueError, KeyError, ValidationError) as e:
            print(f"Failed to validate message {event['content']['body']}")
            print(f"Error: {e}")
            pass
        self._handle_message_DTO(message_obj, room_id)
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

    def _handle_message_DTO(self, message_dto: MessageDTO, wallet_id: str):
        """ Handles a message DTO. """
        print(f"Message received: {message_dto}")
        try:
            if message_dto.type == MessageType.TransactionRequest:
                print(f"Transaction request received: {message_dto.data}")
                transaction_request_obj: TransactionDTO = message_dto.data
                TransactionService.handler_new_transaction(transaction_request_obj)
                return
            
            elif message_dto.type == MessageType.TransactionResponse:
                print(f"Transaction response received: {message_dto.data}")
                transaction_response_obj: TransactionResponseDTO = message_dto.data
                return TransactionService.handle_incoming_transaction_response(transaction_response_obj)
        
            elif message_dto.type == MessageType.UserPublicShare:
                print(f"User public share received: {message_dto.data}")
                user_public_share_obj: user_public_share = message_dto.data
                return UserShareService.handle_incoming_public_share(user_public_share_obj, wallet_id)
            
            elif message_dto.type == MessageType.KeyGenerationShare:
                key_generation_share_obj: wallet_key_generation_share = message_dto.data
                print(f"Key generation share received: {key_generation_share_obj}")
                return UserShareService.handle_incoming_key_generation_share(key_generation_share_obj)
                
            elif message_dto.type == MessageType.Commitment:
                commitment_obj = message_dto.data
                print(f"Commitment received: {commitment_obj}")

            
            elif message_dto.type == MessageType.WalletGenerationMessage:
                wallet_generation_message_obj = message_dto.data
                print(f"Wallet generation message received: {wallet_generation_message_obj}")
            
            elif message_dto.type == MessageType.ValueKnowledgeZkProof:
                value_knowledge_zk_proof_obj = message_dto.data
                print(f"Value knowledge ZK proof received: {value_knowledge_zk_proof_obj}")
            
            elif message_dto.type == MessageType.MtaChallenge:
                mta_challenge_obj = message_dto.data
                print(f"MTA challenge received: {mta_challenge_obj}")
            
            elif message_dto.type == MessageType.MtaCommitmentAlice:
                mta_commitment_alice_obj = message_dto.data
                print(f"MTA commitment Alice received: {mta_commitment_alice_obj}")
            
            elif message_dto.type == MessageType.MtaCommitmentBob:
                mta_commitment_bob_obj = message_dto.data
                print(f"MTA commitment Bob received: {mta_commitment_bob_obj}")
            
            elif message_dto.type == MessageType.MtaProofForChallengeAlice:
                mta_proof_for_challenge_alice_obj = message_dto.data
                print(f"MTA proof for challenge Alice received: {mta_proof_for_challenge_alice_obj}")
            
            elif message_dto.type == MessageType.MtaProofForChallengeBob:
                mta_proof_for_challenge_bob_obj = message_dto.data
                print(f"MTA proof for challenge Bob received: {mta_proof_for_challenge_bob_obj}")
            elif message_dto.type == MessageType.MtaWcCommitmentBob:
                mta_wc_commitment_bob_obj = message_dto.data
                print(f"MTA WC commitment Bob received: {mta_wc_commitment_bob_obj}")
            else:
                print(f"Unknown message type: {message_dto.type}")
                return
            
        except ValidationError as e:
            print(f"Validation error: {e}")
            return
            