import os
from dotenv import load_dotenv

load_dotenv()

class User():
    matrix_id: str
    email: str
    password: str

class Test():
    class User1(User):
        matrix_id = os.getenv('USER_ID1', "user1")
        email = os.getenv('USER_EMAIL1')
        password = os.getenv('USER_PASSWORD1')

    class User2(User):
        matrix_id = os.getenv('USER_ID2', "user2")
        email = os.getenv('USER_EMAIL2')
        password = os.getenv('USER_PASSWORD2')

HOMESERVER_URL = os.getenv('HOMESERVER_URL',"https://matrix.org" )

is_test = os.getenv('IS_TEST', "False") == "True"
DB_FILE1 = os.getenv('DB_FILE1', "local_db1.sqlite")
DB_FILE2 = os.getenv('DB_FILE2', "local_db2.sqlite")