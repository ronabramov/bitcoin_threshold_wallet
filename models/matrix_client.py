from nio import AsyncClient, LoginResponse
import asyncio

class MatrixClient:
    def __init__(self, homeserver_url, username, password):
        self.client = AsyncClient(homeserver_url, username)
        self.username = username
        self.password = password

    async def login(self):
        response = await self.client.login(self.password)
        if isinstance(response, LoginResponse):
            print(f"Logged in as {self.username}")
        else:
            print(f"Login failed: {response}")
            raise Exception("Matrix login failed")
    
    async def join_room(self, room_id):
        response = await self.client.join(room_id)
        if response:
            print(f"Joined room: {room_id}")
        else:
            print(f"Failed to join room: {response}")
    
    async def send_message(self, room_id, message):
        response = await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        if response:
            print(f"Message sent to room {room_id}")
        else:
            print(f"Failed to send message: {response}")
    
    async def close(self):
        await self.client.close()

# Example usage
async def main():
    client = MatrixClient("https://matrix.org", "your_username", "your_password")
    await client.login()
    await client.join_room("!yourRoomId:matrix.org")
    await client.send_message("!yourRoomId:matrix.org", "Hello, Matrix!")
    await client.close()

# Run the example
if __name__ == "__main__":
    asyncio.run(main())

