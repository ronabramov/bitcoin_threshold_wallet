import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from local_db.sql_db_dal import get_all_user_friends, insert_new_friend

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/friends", tags=["friends"])

class Friend(BaseModel):
    email: str
    matrix_id: str

@router.get("/")
async def get_friends():
    try:
        friends = get_all_user_friends()
        return friends
    except Exception as e:
        logger.error(f"Error fetching friends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch friends")

@router.post("/")
async def add_friend(friend: Friend):
    try:
        new_friend = insert_new_friend(user_email=friend.email, user_matrix_id=friend.matrix_id)
        return new_friend
    except Exception as e:
        logger.error(f"Error adding friend: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add friend")

