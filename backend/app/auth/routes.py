from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

# TEMP in-memory user (we’ll move to DB next step)
FAKE_USER = {
    "username": "user1",
    "hashed_password": hash_password("password123"),
    "role": "customer"
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    if data.username != FAKE_USER["username"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, FAKE_USER["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": data.username, "role": FAKE_USER["role"]})
    return {"access_token": token, "token_type": "bearer"}
