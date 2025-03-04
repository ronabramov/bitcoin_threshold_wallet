import common_utils
from  local_db.sql_db import DB, User
import bcrypt
from local_db.sql_db_dal import get_user_by_email, add_user
from fastapi import HTTPException
from Services.Context import Context
from Services.MatrixService import MatrixService
from Services.MatrixListenerService import MatrixRoomListener

def hash_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def login_user(email: str, matrix_user_id: str, password: str) :
    """Verify user credentials against the database."""
    
    # maybe user is not registered in the database
    user = get_user_by_email(email)
    
    if user is None:
        register_new_user(email=email, matrix_user_id=matrix_user_id, password=password)
    elif not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
        Context.set(matrix_user_id, password)
        matrix_client = MatrixService.instance().client
        listener = MatrixRoomListener(matrix_client)
        listener.start_listener()
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    

def register_new_user(email: str, matrix_user_id: str, password: str) -> bool:
    """Register a new user in the database."""
    hashed_password = hash_password(password)
    return add_user(email, hashed_password, matrix_user_id)

