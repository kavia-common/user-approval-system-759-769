from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.db.database import get_db, fetch_all_dicts, fetch_one_dict, paginate_query
from src.models.schemas import UserCreate, UserOut, UserUpdate
from src.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, summary="Create user", operation_id="create_user")
# PUBLIC_INTERFACE
def create_user(payload: UserCreate, _user=Depends(get_current_user)):
    """Create a new user."""
    with get_db() as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (email, name, role) VALUES (?, ?, ?)",
                (payload.email, payload.name, "user"),
            )
            user_id = c.lastrowid
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        c.execute("SELECT id, email, name, role FROM users WHERE id = ?", (user_id,))
        row = fetch_one_dict(c)
        assert row
        return row


@router.get("", response_model=List[UserOut], summary="List users", operation_id="list_users")
# PUBLIC_INTERFACE
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    _user=Depends(get_current_user),
):
    """List users with pagination."""
    with get_db() as conn:
        c = conn.cursor()
        base = "SELECT id, email, name, role FROM users ORDER BY id DESC"
        sql, params = paginate_query(base, tuple(), page, page_size)
        c.execute(sql, params)
        return fetch_all_dicts(c)


@router.get("/{user_id}", response_model=UserOut, summary="Get user by id", operation_id="get_user")
# PUBLIC_INTERFACE
def get_user(user_id: int, _user=Depends(get_current_user)):
    """Get a user by id."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, email, name, role FROM users WHERE id = ?", (user_id,))
        row = fetch_one_dict(c)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return row


@router.patch("/{user_id}", response_model=UserOut, summary="Update user", operation_id="update_user")
# PUBLIC_INTERFACE
def update_user(user_id: int, payload: UserUpdate, _user=Depends(get_current_user)):
    """Update user name or role."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not c.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if payload.name is not None:
            c.execute("UPDATE users SET name = ? WHERE id = ?", (payload.name, user_id))
        if payload.role is not None:
            c.execute("UPDATE users SET role = ? WHERE id = ?", (payload.role, user_id))
        c.execute("SELECT id, email, name, role FROM users WHERE id = ?", (user_id,))
        return fetch_one_dict(c)


@router.delete("/{user_id}", summary="Delete user", operation_id="delete_user")
# PUBLIC_INTERFACE
def delete_user(user_id: int, _user=Depends(get_current_user)):
    """Delete a user."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"status": "deleted"}
