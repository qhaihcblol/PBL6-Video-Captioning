from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserWithToken
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserWithToken:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data (email, password, full_name)

        Returns:
            UserWithToken object with user info and JWT token

        Raises:
            HTTPException 400: If email already exists
        """
        # Check if user with email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hashed_password,
            is_active=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT token
        token = create_access_token(
            data={"user_id": str(new_user.id), "email": new_user.email}
        )

        # Return user with token
        return UserWithToken(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            token=token,
            message="Registration successful",
        )

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> UserWithToken:
        """
        Authenticate user and generate JWT token.

        Args:
            db: Database session
            login_data: Login credentials (email, password)

        Returns:
            UserWithToken object with user info and JWT token

        Raises:
            HTTPException 401: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()

        # Check if user exists and password is correct
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
            )

        # Generate JWT token
        token = create_access_token(data={"user_id": str(user.id), "email": user.email})

        # Return user with token
        return UserWithToken(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            token=token,
            message="Login successful",
        )

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email address"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
