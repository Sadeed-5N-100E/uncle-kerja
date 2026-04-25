"""
Auth — dual-mode authentication.

Mode 1 (demo, always works):
  Two hardcoded accounts signed with a local JWT secret.
  admin@demo.local / Admin@1234  → role: admin
  user@demo.local  / User@1234   → role: user

Mode 2 (Supabase, when configured):
  POST /api/auth/signup  creates a real Supabase user.
  POST /api/auth/login   exchanges email+password for Supabase JWT.
  Works after disabling "Confirm email" in Supabase Dashboard → Auth → Settings.

The same FastAPI dependency (require_auth) works for both modes —
it tries Supabase first, falls back to local JWT.
"""
from __future__ import annotations
import os, logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
import httpx
from jose import jwt, JWTError
from fastapi import Header, HTTPException

load_dotenv(Path(__file__).parents[2] / ".env")
log = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY", "")
JWT_SECRET   = os.getenv("JWT_SECRET", "careercop-demo-secret-2026")
ALGORITHM    = "HS256"

# ── Demo accounts (hardcoded for hackathon) ───────────────────────────────────
_DEMO_USERS = {
    "admin@demo.local": {"password": "Admin@1234", "role": "admin", "id": "demo-admin-001"},
    "user@demo.local":  {"password": "User@1234",  "role": "user",  "id": "demo-user-001"},
}


def _make_local_token(user: dict) -> str:
    payload = {
        "sub":   user["id"],
        "email": user["email"],
        "role":  user["role"],
        "exp":   datetime.now(timezone.utc) + timedelta(hours=12),
        "mode":  "local",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def _verify_local_token(token: str) -> dict | None:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return {"id": data["sub"], "email": data["email"], "role": data["role"]}
    except JWTError:
        return None


# ── Supabase helpers ──────────────────────────────────────────────────────────

def _sb_headers():
    return {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
    }


def _sb_shape(raw: dict) -> dict:
    u = raw.get("user") or {}
    return {
        "access_token":  raw.get("access_token", ""),
        "refresh_token": raw.get("refresh_token", ""),
        "user": {
            "id":    u.get("id"),
            "email": u.get("email"),
            "role":  (u.get("user_metadata") or {}).get("role", "user"),
        },
    }


# ── Public API ────────────────────────────────────────────────────────────────

def signup(email: str, password: str, role: str = "user") -> dict:
    """Create a new user. Tries Supabase first, falls back to local store for demo accounts."""
    if email in _DEMO_USERS:
        raise ValueError("This email is reserved for demo accounts.")
    if not SUPABASE_URL:
        raise ValueError("Supabase not configured.")
    resp = httpx.post(
        f"{SUPABASE_URL}/auth/v1/signup",
        headers=_sb_headers(),
        json={"email": email, "password": password, "data": {"role": role}},
        timeout=10,
    )
    if resp.status_code not in (200, 201):
        raise ValueError(resp.json().get("msg") or resp.json().get("error_description") or resp.text)
    return _sb_shape(resp.json())


def login(email: str, password: str) -> dict:
    """
    Sign in. Checks demo accounts first (instant, no network),
    then tries Supabase.
    """
    # Demo accounts
    demo = _DEMO_USERS.get(email)
    if demo:
        if demo["password"] != password:
            raise ValueError("Invalid credentials")
        user = {"id": demo["id"], "email": email, "role": demo["role"]}
        token = _make_local_token(user)
        return {"access_token": token, "refresh_token": "", "user": user}

    # Supabase
    if not SUPABASE_URL:
        raise ValueError("Invalid credentials")
    resp = httpx.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=_sb_headers(),
        json={"email": email, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        raise ValueError(resp.json().get("error_description") or "Invalid credentials")
    return _sb_shape(resp.json())


def get_user(access_token: str) -> dict | None:
    """Validate token — tries local JWT first, then Supabase."""
    # Local JWT
    local = _verify_local_token(access_token)
    if local:
        return local
    # Supabase JWT
    if not SUPABASE_URL:
        return None
    try:
        resp = httpx.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {access_token}"},
            timeout=8,
        )
        if resp.status_code != 200:
            return None
        raw = resp.json()
        return {
            "id":    raw.get("id"),
            "email": raw.get("email"),
            "role":  (raw.get("user_metadata") or {}).get("role", "user"),
        }
    except Exception:
        return None


# ── FastAPI dependencies ──────────────────────────────────────────────────────

def require_auth(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    user = get_user(authorization.split(" ", 1)[1])
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


def require_admin(authorization: str = Header(...)) -> dict:
    user = require_auth(authorization)
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return user
