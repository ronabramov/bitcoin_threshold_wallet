from fastapi import APIRouter
from pydantic import BaseModel
from Services.UsersService import login_user

class LoginRequest(BaseModel):
    email: str
    matrix_user_id: str
    password: str

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest):
    return login_user(email=request.email, matrix_user_id=request.matrix_user_id, password=request.password)

