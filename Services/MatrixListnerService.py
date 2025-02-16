from matrix_client.client import MatrixClient
from matrix_client.room import Room
import time


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
