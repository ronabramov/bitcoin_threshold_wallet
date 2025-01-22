from matrix_client.client import MatrixClient
import common_utils
import requests

HOMESERVER_URL = "https://matrix.org"

def create_matrix_cleint(matrix_user_id : str , matrix_user_password):
    client = MatrixClient(HOMESERVER_URL)
    # Log in as the admin      
    token = client.login_with_password(username=matrix_user_id, password=matrix_user_password)
    print(f"Admin logged in successfully. Token: {token}")

def create_room(room_name : str, matrix_client : MatrixClient):
    new_room = matrix_client.create_room(alias=room_name)
    # TODO : implement saving the new room in the local db.
    #        make all rooms creation use that method. 
    #        This is mainly required in case of new wallet, consider other cases 

def send_message_to_wallet_room(room_id: str, message: str, admin_user: str | None = None, admin_password: str | None = None, client : MatrixClient | None = None): #Here is some of sdk work with examples.
    """Send a message to the Matrix room for a wallet."""

    try:
        if not client : 
            client = MatrixClient(HOMESERVER_URL)
            # Log in as the admin
            token = client.login_with_password(username=admin_user, password=admin_password)
            print(f"Admin logged in successfully. Token: {token}")

        # Retrieve the room and send a message
        room = client.join_room(room_id)
        room.send_text(message)
        print(f"Message sent to room {room_id}: {message}")

        new_room = client.create_room(alias=f"new_room_for_test_11112222222111111231", is_public=False)
        new_room_id = new_room.room_id
        print(f"the new room id is {new_room_id}")
        x = client.join_room(new_room_id)
        new_room.send_text(f"{message} and this is meeee")
        check = True

    except Exception as e:
        print(f"Error sending message to room: {e}")

def create_user_backup_room(admin_user_name: str, admin_password: str):
    client = MatrixClient(HOMESERVER_URL)
    try:
        token = client.login_with_password(username=admin_user, password=admin_password)
        print(f"Admin logged in successfully. Token: {token}")
        backup_room = client.create_room(alias=f"remote_user_backup_{admin_user_name}", is_public=False)
        room_id = backup_room.room_id
        client.join_room(room_id)
        encrypted_password = common_utils.hash_password(admin_password)
        save_data_to_backup({admin_user_name, encrypted_password, token, room_id}, client, backup_room)
        client.logout()
    except Exception as e:
        print(f"Error creating backup room to user {admin_user_name}: {e}")

def save_data_to_backup(data : list, client : MatrixClient, room):
    for message in data:
        try:
            room.send_text(message)
        except Exception as e:
            print(f"Failed saving {message} to backup server : {e}")

def get_room_history(room_id, admin_user, admin_password, num_of_meesages_to_retrieve):
    client = MatrixClient(HOMESERVER_URL)
    token = client.login_with_password(username=admin_user, password=admin_password)
    url = f"{HOMESERVER_URL}/_matrix/client/v3/rooms/{room_id}/messages"
    params = {
        "dir": "b",  # Retrieve messages in reverse (backward)
        "limit": num_of_meesages_to_retrieve  # Number of messages to fetch
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        messages = response.json()["chunk"]
        for message in messages:
            if message["type"] == "m.room.message":
                print(f"{message['sender']}: {message['content']['body']}")
    else:
        print(f"Failed to retrieve messages: {response.status_code} - {response.text}")

def send_private_message_to_user(target_user_matrix_id : str , message : str):
    client = MatrixClient(HOMESERVER_URL)
    client.login_with_password(username=admin_user, password=admin_password)
    rooms = client.rooms
    target_room_id = None
    for room_id in rooms:
        room = client.join_room(room_id)
        members = room._members
        if target_user_matrix_id in members and len(members) == 2:
            target_room_id = room_id
            break
    if not target_room_id:
        new_room = client.create_room(alias= f"private_room_for_{admin_user}_and_{target_user_matrix_id}")
        target_room_id = new_room.room_id
    
    private_room = client.join_room(target_room_id)
    private_room.send_text(message)
    print(f"Successfuly sent private message in room {target_room_id}")

# Example usage
if __name__ == "__main__":
    room_id = "!oSvtQooUmWSlmdjZkP:matrix.org"
    message = "Hello, Wallet Members!"
    admin_user = "ron_test"
    admin_password = "Roniparon32"
    user_matrix_id = '@ron_test:matrix.org'
    destination_user_matrix_id = '@ronabramovich:matrix.org'
    send_private_message_to_user(destination_user_matrix_id, "This is a privatenessage")
    create_user_backup_room(admin_user, admin_password)
    get_room_history(room_id, admin_user, admin_password)
    send_message_to_wallet_room(room_id, message, admin_user, admin_password)
