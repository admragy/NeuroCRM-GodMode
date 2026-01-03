"""
API Dependencies - Shared dependencies for FastAPI routes
Includes authentication, database session, and WebSocket security
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, WebSocket, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

# Security scheme for API endpoints
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_ws_current_user(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
) -> int:
    """
    Verify WebSocket connection authentication
    Extracts and validates JWT token from query parameter
    
    Usage:
        @app.websocket("/ws")
        async def websocket_endpoint(
            websocket: WebSocket,
            user_id: int = Depends(get_ws_current_user)
        ):
            # user_id is now authenticated and verified
    """
    # Verify JWT token
    payload = verify_token(token, "access")
    
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Extract user_id
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return int(user_id)


async def get_current_org_id(
    current_user: User = Depends(get_current_user)
) -> int:
    """
    Extract organization ID from current user
    Used for multi-tenant data isolation
    """
    if not hasattr(current_user, 'organization_id') or not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization"
        )
    
    return current_user.organization_id


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a superuser/admin
    """
    if not getattr(current_user, 'is_superuser', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


class OrgFilter:
    """
    Automatic organization filtering for multi-tenant isolation
    """
    def __init__(self, org_id: int = Depends(get_current_org_id)):
        self.org_id = org_id
    
    def filter_dict(self) -> dict:
        """Return filter as dictionary"""
        return {"organization_id": self.org_id}
    
    def __call__(self) -> int:
        """Return organization ID"""
        return self.org_id
