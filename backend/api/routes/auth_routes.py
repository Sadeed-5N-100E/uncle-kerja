from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr
from core.auth import signup, login, get_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthRequest(BaseModel):
    email: str
    password: str
    role: str = "user"   # "admin" or "user"


@router.post("/signup")
def do_signup(req: AuthRequest):
    try:
        return signup(req.email, req.password, req.role)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/login")
def do_login(req: AuthRequest):
    try:
        return login(req.email, req.password)
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.get("/me")
def me(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    user = get_user(authorization.split(" ", 1)[1])
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user
