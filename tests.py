from registration import create_user_homeserver_with_db_registration

async def test_create_user_homeserver_with_db_registration():
    username = "testuser"
    password = "securepassword123"
    email = "testuser@example.com"

    try:
        result = create_user_homeserver_with_db_registration(username, password, email)
        print(f"Test Successful: {result}")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    x = test_create_user_homeserver_with_db_registration()
