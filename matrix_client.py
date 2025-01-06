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
            raise Exception(f"Failed to login: {response}")

    async def send_message(self, room_id: str, message: str):
        response = await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        return response

    async def logout(self):
        await self.client.logout()
        await self.client.close()
