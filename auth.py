# auth.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import os


# Security settings
SECRET_KEY = "e3a7b1c8d2f90465381297e6a4b0d3c1f8e5a2d9b7c4e1f0a3b8d6c9e2f1a4d5"  # Use a fixed, strong value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increased for testing

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password, hashed_password):
    """Verify password against stored hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(
        f"Created token for user ID {data.get('sub')}, token starts with: {encoded_jwt[:10]}..."
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    from database import get_db

    print(f"*** GET_CURRENT_USER INVOKED (for /movies?) ***")
    print(f"Token (first 10 chars): {token[:10]}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        print("Attempting to decode token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        print(f"TOKEN DECODED SUCCESSFULLY - User ID from token: {user_id}")
        if user_id is None:
            print("ERROR: Token missing 'sub' claim")
            raise credentials_exception
    except JWTError as e:
        print(f"JWT DECODE ERROR: {str(e)}")
        raise credentials_exception

    # Get user from database
    db = get_db()
    try:
        # Important: Use the user_id as a string for the query initially
        print(f"Attempting to find user with ID (string): {user_id}")
        user_obj_id = ObjectId(user_id)
        print(f"Attempting to find user with ObjectId: {user_obj_id}")

        print("Executing database query for user...")
        user = await db.users.find_one({"_id": user_obj_id})

        if user is None:
            print(f"ERROR: User NOT FOUND in database with ID: {user_id}")
            raise credentials_exception
        else:
            print(f"USER FOUND IN DATABASE - Username: {user['username']}")

        # Add both string versions of the ID for compatibility
        user["id"] = str(user["_id"])

        if "_id" in user and isinstance(user["_id"], ObjectId):
            print(f"User has _id as ObjectId: {user['_id']}")
        else:
            print(f"WARNING: User _id not found or not ObjectId")

    except Exception as e:
        print(f"DATABASE ERROR during user lookup: {str(e)}")
        raise credentials_exception

    print("*** GET_CURRENT_USER COMPLETED ***")
    return user
