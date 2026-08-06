import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("AUTH_SECRET", "development-only-secret-change-before-deploy")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from OAuth2 scheme first, then from Authorization header
    if not token and authorization:
        token = get_token_from_header(authorization)
    
    print(f"DEBUG: Token from OAuth2: {token[:20] if token else None}...")
    print(f"DEBUG: Authorization header: {authorization[:30] if authorization else None}...")
    print(f"DEBUG: Final token: {token[:20] if token else None}...")
    
    if not token:
        print("DEBUG: No token found, raising exception")
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        # Handle string user_id from JWT (user.id is now sent as str in main.py)
        user_id = int(subject) if subject is not None else None
        print(f"DEBUG: Decoded payload, user_id: {user_id}")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError) as e:
        print(f"DEBUG: JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    print(f"DEBUG: Found user: {user.username if user else None}")
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
