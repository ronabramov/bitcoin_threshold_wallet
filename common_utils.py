import bcrypt

def hash_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_matrix_user(email : str, user_name : str, password: str):
    #Here we should take the user to the element's UI, to follow registration process. Finally we would need to save the username
    #Place holder for connecting new user
    return (user_name,password)