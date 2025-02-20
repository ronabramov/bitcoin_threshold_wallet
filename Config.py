import os
from dotenv import load_dotenv

load_dotenv()
class TEST():
    class USER1():
        user_matrix_id = os.getenv('USER_ID1')
        password = os.getenv('USER_PASSWORD1')

    class USER2():
        user_matrix_id = os.getenv('USER_ID2')
        password = os.getenv('USER_PASSWORD2')

HOMESERVER_URL = os.getenv('HOMESERVER_URL',"https://matrix.org" )