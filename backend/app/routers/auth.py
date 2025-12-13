from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserWithToken, UserResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post(
    "/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    **Required fields:**
    - `email`: Valid email address (will be validated)
    - `password`: Minimum 8 characters
    - `full_name`: User's full name

    **Returns:**
    - User information with JWT token

    **Error codes:**
    - `400`: Email already registered
    - `422`: Validation error (invalid email, password too short, etc.)
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=UserWithToken)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and get JWT token.

    **Required fields:**
    - `email`: User's email address
    - `password`: User's password

    **Returns:**
    - User information with JWT token

    **Error codes:**
    - `401`: Invalid credentials (wrong email or password)
    - `403`: User account is inactive

    **Usage:**
    Use the returned token in subsequent requests:
    ```
    Authorization: Bearer <token>
    ```
    """
    return AuthService.login_user(db, login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.

    **Requires authentication:** Bearer token in Authorization header

    **Returns:**
    - Current user's profile information

    **Error codes:**
    - `401`: Invalid or expired token
    - `403`: User account is inactive

    **Example:**
    ```
    GET /api/auth/me
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should delete token).

    **Note:** JWT tokens are stateless, so logout is handled client-side
    by deleting the stored token. This endpoint exists for consistency
    and can be extended to implement token blacklisting if needed.

    **Requires authentication:** Bearer token in Authorization header

    **Returns:**
    - Success message
    """
    return {
        "message": "Logout successful",
        "detail": "Please delete the token from client storage",
    }
