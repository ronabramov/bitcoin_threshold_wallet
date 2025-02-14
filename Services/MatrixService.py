from matrix_client.client import MatrixClient
from matrix_client.room import Room
from matrix_client.user import User
import common_utils
import requests
import json
from typing import List
import time

HOMESERVER_URL = "https://matrix.org" # Should be part of the user details. 

# should be in a config file - in  a local db or run time instance
matrix_user_id = "ron_test"
matrix_user_password = "Roniparon32"


class MatrixService:
    _instance = None

    def __init__(self):
        if MatrixService._instance is not None:
            raise Exception(
                "This class is a singleton! Use MatrixService.instance to access it."
            )
        self.matrix_user_id = matrix_user_id
        self.matrix_user_password = matrix_user_password
        self._client = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def client(self) -> MatrixClient:
        if self._client and self._client.token:
            return self._client
        client = MatrixClient(HOMESERVER_URL)
        # Log in as the admin
        token = client.login_with_password(
            username=self.matrix_user_id, password=self.matrix_user_password
        )
        print(f"Admin logged in successfully. Token: {token}")
        self._client = client
        return client

    def create_new_room_and_invite_users(self, room_name : str, users_Ids : List[str]):
        """
        Create new room and invite users
        """
        new_room : Room = self.create_room(room_name) 
        self.invite_users_to_room(new_room, users=users_Ids)
        return new_room.room_id

    def create_room(self, room_name: str):
        new_room = self.client.create_room(alias=room_name)
        return new_room

    def invite_users_to_room(self, room: Room, users: List[str]):
        print(f"adding users to room {room.room_id}")
        for user in users:
            # add try catch
            try:
                print(f"Inviting user {user} to room")
                room.invite_user(user)
            except Exception as e:
                print(f"Error inviting user {user} to room: {e}")
        
    def send_message_to_wallet_room(self, room_id: str, message: str) -> bool:
        """Send a message to the Matrix room for a wallet."""
        try:
            room = self.client.join_room(room_id)
            room.send_text(message)
            print(f"Message sent to room {room_id}: {message}")
            return True
        except Exception as e:
            print(f"Error sending message to room: {e}")
            return False

    def create_user_backup_room(self):
        try:
            backup_room: Room = self.client.create_room(
                alias=f"remote_user_backup_{self.matrix_user_id}", is_public=False
            )
            room_id = backup_room.room_id
            self.client.join_room(room_id)
            encrypted_password = common_utils.hash_password(self.matrix_user_password)
            self.save_data_to_backup(
                {self.matrix_user_id, encrypted_password, self.client.token, room_id},
                backup_room,
            )
            self.client.logout()
        except Exception as e:
            print(f"Error creating backup room to user {self.matrix_user_id}: {e}")

    def save_data_to_backup(self, data: list, room: Room):
        for message in data:
            try:
                room.send_text(message)
            except Exception as e:
                print(f"Failed saving {message} to backup server : {e}")

    def get_room_history(self, room_id: str, num_of_messages_to_retrieve: int = 20):
        token = self.client.token
        url = f"{HOMESERVER_URL}/_matrix/client/v3/rooms/{room_id}/messages"
        params = {
            "dir": "b",  # Retrieve messages in reverse (backward)
            "limit": num_of_messages_to_retrieve,  # Number of messages to fetch
        }
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            messages = response.json()["chunk"]
            for message in messages:
                if message["type"] == "m.room.message":
                    print(f"{message['sender']}: {message['content']['body']}")
        else:
            print(
                f"Failed to retrieve messages: {response.status_code} - {response.text}"
            )

    def __user_matrix_id_to_room_name(self, user_matrix_id: str):
        return user_matrix_id.replace(":", "_")

    def __get_private_room_with_user(self, target_user_matrix_id: str) -> Room:
        rooms = self.client.rooms
        target_room: Room = None
        room: Room
        for room in rooms.values():
            members: List[User] = room.get_joined_members()
            if (
                members
                and len(members) == 2
                and target_user_matrix_id in [member.user_id for member in members]
            ):
                target_room = room
                print(
                    f"Found private room with user {target_user_matrix_id} in room {room.room_id}"
                )
                break
            
            target_room = self.__get_private_room_with_user_from_events(target_user_matrix_id, room)    

        if not target_room:
            unix_timestamp = int(time.time())
            room_name = f"private_room_for_{self.__user_matrix_id_to_room_name(self.matrix_user_id)}_and_{self.__user_matrix_id_to_room_name(target_user_matrix_id)}_{unix_timestamp}"
            new_room: Room = self.client.create_room(
                alias=room_name, invitees=[target_user_matrix_id]
            )
            target_room = new_room
        return target_room
    
    def __get_private_room_with_user_from_events(self, target_user_matrix_id: str, room: Room) -> Room:
        for event in room.events:
            if (
                event['type'] == "m.room.invite"
                and event['content']['membership'] == "invite"
                and target_user_matrix_id == event['state_key']
            ):
                print(
                    f"Found private room with user {target_user_matrix_id} in room {room.room_id}"
                )
                return room
        return None
    
    def send_private_message_to_user(self, target_user_matrix_id: str, message: str):
        target_room: Room = self.__get_private_room_with_user(target_user_matrix_id)
        target_room.send_text(message)
        print(f"Successfuly sent private message in room {target_room.room_id}")
    
    def fetch_pending_invited_rooms(self):
        rooms = self.client.invited_rooms
        # TODO : Required Fix.
        # pending_rooms for room in rooms.values():
        #     if room.invite_state == "invite":
        #         print(f"Room {room.room_id} is pending invitation")
        #         return room
        return None


# Example usage
if __name__ == "__main__":
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    destination_user_matrix_id = "@ronabramovich:matrix.org"
    message = {"body": "This is a privatenessage"}
    MatrixService.instance().send_private_message_to_user(
        destination_user_matrix_id, "This is a privatenessage"
    )
    MatrixService.instance().create_user_backup_room()
    MatrixService.instance().get_room_history(room_id)
    MatrixService.instance().send_message_to_wallet_room(room_id, message)
    room = MatrixService.instance().create_room("test_room_new")
    MatrixService.instance().invite_users_to_room(room, [destination_user_matrix_id])
    
    
    # TODO create room with invite_only=true - only invited users can join