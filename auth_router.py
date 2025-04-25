# auth_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from auth_models import UserCreate, UserLogin, UserResponse, TokenResponse
from datetime import datetime
from bson import ObjectId

auth_router = APIRouter()


@auth_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate):
    """Register a new user"""
    db = get_db()

    print(f"Registration attempt for user: {user.username}")

    # Check if username already exists
    if await db.users.find_one({"username": user.username}):
        print(f"Username already exists: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    if await db.users.find_one({"email": user.email}):
        print(f"Email already exists: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create user document
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()

    # Insert into database
    result = await db.users.insert_one(user_dict)
    print(f"User created with ID: {result.inserted_id}")

    # Get the created user
    created_user = await db.users.find_one({"_id": result.inserted_id})

    # Format response
    created_user["id"] = str(created_user["_id"])
    print(f"User registered successfully: {user.username}")

    return created_user


@auth_router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    db = get_db()

    print(f"Login attempt for user: {form_data.username}")

    # Find user by username
    user = await db.users.find_one({"username": form_data.username})
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    valid_password = verify_password(form_data.password, user["password"])
    print(f"Password validation result: {valid_password}")

    if not valid_password:
        print(f"Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})

    print(f"Login successful for user: {form_data.username}")
    print(f"Token length: {len(access_token)}")
    print(f"Token starts with: {access_token[:15]}...")

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current logged in user info"""
    print(f"Get current user info for: {current_user['username']}")
    return current_user
