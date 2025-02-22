from matrix_client.client import MatrixClient
from matrix_client.room import Room
from matrix_client.user import User
#Should put commoun_utils and models dto import in comment for direct debug.
import common_utils
from models.DTOs.message_dto import MessageDTO
import requests
import random   
from typing import List
import time
from pydantic import ValidationError
import sys
import os
import Config 
## FOR DEBUGGING MATRIX SERVICE DIRECTLY:
# # Get the absolute path of the project root
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# # Add the project root to Python's sys.path
# sys.path.insert(0, PROJECT_ROOT)

# # Now import your modules
# from models.DTOs.message_dto import MessageDTO


MATRIX_MESSAGES_MAIN_NODE = "chunk"
MATRIX_PROPERTY_FOR_MESSAGES_TRACKING = "end" # If exists, this is token for next messages. Otherwise, no further messages exists.


# should be in a config file - in  a local db or run time instance

class Context():
    _matrix_user_id = ""
    _matrix_user_password = ""
    @staticmethod
    def set(matrix_user_id : str, matrix_user_password : str):
        Context._matrix_user_id = matrix_user_id
        Context._matrix_user_password = matrix_user_password
        MatrixService.instance().matrix_user_id = matrix_user_id
        MatrixService.instance().matrix_user_password = matrix_user_password
        MatrixService.instance()._instance = None
    
    @property
    def matrix_user_id(self):
        return self._matrix_user_id
    
    @property
    def matrix_user_password(self):
        return self._matrix_user_password
    


class MatrixService:
    _instance = None

    def __init__(self):
        if MatrixService._instance is not None:
            raise Exception(
                "This class is a singleton! Use MatrixService.instance to access it."
            )
        self.matrix_user_id = Context._matrix_user_id
        self.matrix_user_password = Context._matrix_user_password
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
        client = MatrixClient(Config.HOMESERVER_URL)
        # Log in as the admin
        token = client.login(
            username=self.matrix_user_id, password=self.matrix_user_password, sync=True
        )
        print(f"Admin logged in successfully. Token: {token}")
        self._client = client
        return client

    def create_new_room_and_invite_users(self, room_name : str, users_Ids : List[str], first_message : str = None):
        """
        Create new room and invite users
        """
        new_room : Room = self.create_room(room_name) 
        self.client.join_room(new_room.room_id)
        room_id = new_room.room_id
        self.invite_users_to_room(new_room, users=users_Ids)
        
        if first_message is not None:
            self.send_message_to_wallet_room(room_id=room_id, message=first_message)

        return room_id

    def create_room(self, room_name: str):
        new_room = self.client.create_room(alias=f"{room_name}_{random.randint(1,100000)}")
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
    
    def join_room_invitation(self, room_id):
        """
        Return room's name
        """
        room : Room = self.client.join_room(room_id_or_alias=room_id)
        return room.name

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
            "dir": "b",
            "limit": num_of_messages_to_retrieve,
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
    
    def fetch_pending_invited_rooms(self) -> List[Room]:
        rooms = self.client.invited_rooms
        # TODO : Required Fix.
        # pending_rooms for room in rooms.values():
        #     if room.invite_state == "invite":
        #         print(f"Room {room.room_id} is pending invitation")
        #         return room
        return None
    
    def reject_room_invitation_by_id(self, room_id : str):
        rooms = self.client.invited_rooms
        for room  in rooms.values():
            self.reject_room_invitation(room=room) # Should be fixed

    
    def reject_room_invitation(self, room : Room) -> bool:
        return room.leave()
    
    def get_next_available_index(self, room_id: str) -> bool:
        #NEEDS FIX - NOT loading , Gilad already solved similiar case
        room : Room = self.client.join_room(room_id)
        return len(room.members_displaynames)
    
    def get_valid_json_messages(self, room_id, limit=100) -> List[MessageDTO]:
        valid_messages = []
        room = self.client.join_room(room_id_or_alias=room_id)
        prev_batch = room.prev_batch

        while True:
            res = self.client.api.get_room_messages(room.room_id, prev_batch, direction="b", limit=limit)

            # Extract only message events
            chunk = res.get(MATRIX_MESSAGES_MAIN_NODE, [])

            for event in chunk:
                if event.get("type") == "m.room.message":
                    try:
                        message_obj = MessageDTO.model_validate_json(event["content"]["body"])
                        valid_messages.append(message_obj)
                    except (ValueError, KeyError, ValidationError):
                        pass 

            prev_batch = res.get(MATRIX_PROPERTY_FOR_MESSAGES_TRACKING) if MATRIX_PROPERTY_FOR_MESSAGES_TRACKING in res else None
            if not chunk or not prev_batch:
                break
        
        return valid_messages


# # Example usage
# if __name__ == "__main__":
#     room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
#     destination_user_matrix_id = "@ronabramovich:matrix.org"
#     message = {"body": "This is a privatenessage"}
#     # MatrixService.instance().send_private_message_to_user(
#     #     destination_user_matrix_id, "This is a privatenessage"
#     # )
#     messages = MatrixService.instance().get_valid_json_messages(room_id=room_id)
#     print(f' My messages are : {[m for m in messages]} . \n And Thats all ')
#     print('\n \n \n CHECK CHECK \n \n \n')
#     MatrixService.instance().create_user_backup_room()
#     MatrixService.instance().get_room_history(room_id)
#     MatrixService.instance().send_message_to_wallet_room(room_id, message)
#     room = MatrixService.instance().create_room("test_room_new")
#     MatrixService.instance().invite_users_to_room(room, [destination_user_matrix_id])
    
    
#     # TODO create room with invite_only=true - only invited users can join