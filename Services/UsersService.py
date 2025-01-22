
import common_utils
import local_db.sql_db as sql_db


def save_user_data(email: str, password: str, homeserver):
    hashed_password = common_utils.hash_password(password)
    # check if user already exists
    if sql_db.session.query(sql_db.User).filter(sql_db.User.email == email).first():
        print("User already exists")
        return

    sql_db.session.add(
        sql_db.User(
            email=email,
            hashed_password=hashed_password,
            homeserver_url=homeserver["url"],
            homeserver_login=homeserver["login"],
            homeserver_password=homeserver["password"],
        )
    )
    sql_db.session.commit()


def retrieve_users():  # Testing users retival.
    """Retrieve and display all users from the local database."""
    users = sql_db.session.query(sql_db.User).all()
    for user in users:
        print("Email:", user.email)
        print("Hashed Password:", user.hashed_password)
        print("Homeserver URL:", user.homeserver_url)
        print("Homeserver Login:", user.homeserver_login)
        print("Homeserver Password:", user.homeserver_password)
        print("---------------------")

