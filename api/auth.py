
import os
import hashlib
import hmac
import base64
import json

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.config import settings
from api.db import get_db
from api import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def hash_password(plain: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt, 100000)
    return base64.b64encode(salt + hashed).decode('utf-8')

def verify_password(plain: str, hashed_str: str) -> bool:
    try:
        decoded = base64.b64decode(hashed_str)
        salt = decoded[:16]
        stored_hash = decoded[16:]
        computed_hash = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt, 100000)
        return hmac.compare_digest(stored_hash, computed_hash)
    except Exception:
        return False

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def create_token(user_id: int) -> str:
    header = base64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode('utf-8'))
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload_dict = {"sub": str(user_id), "exp": int(expire.timestamp())}
    payload = base64url_encode(json.dumps(payload_dict).encode('utf-8'))
    
    signature = hmac.new(settings.secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{base64url_encode(signature)}"


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> models.User:
    credentials_err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    elif "token" in request.query_params:
        token = request.query_params["token"]
        
    if not token:
        raise credentials_err
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise credentials_err
            
        header, payload, signature = parts
        
        # Verify signature
        expected_sig = hmac.new(settings.secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        
        # Pad strings for base64 decoding
        sig_pad = signature + '=' * (4 - len(signature) % 4)
        if not hmac.compare_digest(base64.urlsafe_b64decode(sig_pad), expected_sig):
            raise credentials_err
            
        payload_pad = payload + '=' * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload_pad))
        
        if datetime.utcnow().timestamp() > data.get("exp", 0):
            raise credentials_err
            
        user_id = data.get("sub")
    except Exception:
        raise credentials_err

    result = await db.execute(select(models.User).where(models.User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_err
    return user
