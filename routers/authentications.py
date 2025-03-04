from fastapi import APIRouter, Response
from pydantic import BaseModel
from Services.UsersService import login_user
from jwt_utils import create_access_token
from fastapi.responses import JSONResponse
import Config 

class LoginRequest(BaseModel):
    email: str
    matrix_user_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response):
    # Authenticate user
    user = login_user(email=request.email, matrix_user_id=request.matrix_user_id, password=request.password)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )
    
    # Create JWT token
    access_token = create_access_token(data={"iss": Config.HOMESERVER_URL , "email": user.email, "matrix_user_id": user.matrix_user_id})
    
    # Set cookie with JWT token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return LoginResponse(
        access_token=access_token
    )

