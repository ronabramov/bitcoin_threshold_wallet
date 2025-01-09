from nio import AsyncClient
from db import users_collection
from datetime import datetime, timezone
from passlib.hash import bcrypt
import requests
import subprocess

RETRY_COUNTS = 3

def create_homeserver(user_id):
    domain = f"user{user_id}.homeserver.com"
    subprocess.run([
        "docker", "run", "-d",
        "--name", f"synapse_{user_id}",
        "-v", f"/data/synapse_{user_id}:/data",
        "-e", f"SYNAPSE_SERVER_NAME={domain}",
        "-e", "SYNAPSE_REPORT_STATS=no",
        "matrixdotorg/synapse:latest"
    ])
    return f"https://{domain}"


def check_homeserver_health(homeserver_url):
    try:
        response = requests.get(f"{homeserver_url}/_matrix/client/versions", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
    
def establish_user_homeserver(user_name):
    success = False
    num_of_tries = 0
    user_homeserver_url = create_homeserver(user_id=user_name)
    while (num_of_tries < RETRY_COUNTS and not success):
        success = check_homeserver_health(user_homeserver_url)
    if not success:
        raise ConnectionRefusedError(f"Couldn't create home_server for user {user_name}")
    return user_homeserver_url

async def register_user(homeserver_url, username, password, email=None):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    if email != None:
        email = bcrypt.hashpw(email.encode(), bcrypt.gensalt()).decode()
    matrix_client = AsyncClient(homeserver_url) # Deploy client to the given homeserver
    try:
        response = await matrix_client.register(username=username, password=password)
        matrix_id = response.user_id
    except Exception as e:
        raise Exception(f"Matrix registration failed: {e}")

    # Store user data in MongoDB
    user_data = {
        "username": username,
        "password_hash": password_hash,
        "homeserver_url": homeserver_url,
        "matrix_id": matrix_id,
        "email": email,
        "created_at": datetime.now(timezone.utc)
    }
    users_collection.insert_one(user_data)

    return {"matrix_id": matrix_id, "homeserver_url": homeserver_url}

async def create_user_homeserver_with_db_registration(username, password, email):
    user_homeserver = establish_user_homeserver(username)
    register_user(homeserver_url=user_homeserver, username=username, password=password, email=email)

