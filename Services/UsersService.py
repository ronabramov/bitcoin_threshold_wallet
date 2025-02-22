
import common_utils
from  local_db.sql_db import DB, User

def save_user_data(email: str, password: str, homeserver):
    hashed_password = common_utils.hash_password(password)
    # check if user already exists
    if DB.session().query(User).filter(User.email == email).first():
        print("User already exists")
        return

    DB.session().add(
        User(
            email=email,
            hashed_password=hashed_password,
            homeserver_url=homeserver["url"],
            homeserver_login=homeserver["login"],
            homeserver_password=homeserver["password"],
        )
    )
    DB.session().commit()


def retrieve_users():  # Testing users retival.
    """Retrieve and display all users from the local database."""
    users = DB.session().query(User).all()
    for user in users:
        print("Email:", user.email)
        print("Hashed Password:", user.hashed_password)
        print("Homeserver URL:", user.homeserver_url)
        print("Homeserver Login:", user.homeserver_login)
        print("Homeserver Password:", user.homeserver_password)
        print("---------------------")

