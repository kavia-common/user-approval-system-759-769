from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.db.database import get_db, fetch_one_dict, fetch_all_dicts, paginate_query
from src.models.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from src.utils.auth import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileOut, summary="Create profile", operation_id="create_profile")
# PUBLIC_INTERFACE
def create_profile(payload: ProfileCreate, _user=Depends(get_current_user)):
    """Create a profile for a user."""
    with get_db() as conn:
        c = conn.cursor()
        # ensure user exists
        c.execute("SELECT id FROM users WHERE id = ?", (payload.user_id,))
        if not c.fetchone():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
        c.execute(
            "INSERT INTO profiles (user_id, bio, avatar_url, location, website) VALUES (?, ?, ?, ?, ?)",
            (payload.user_id, payload.bio or "", payload.avatar_url or "", payload.location or "", payload.website or ""),
        )
        pid = c.lastrowid
        c.execute("SELECT id, user_id, bio, avatar_url, location, website FROM profiles WHERE id = ?", (pid,))
        return fetch_one_dict(c)


@router.get("", response_model=List[ProfileOut], summary="List profiles", operation_id="list_profiles")
# PUBLIC_INTERFACE
def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _user=Depends(get_current_user),
):
    """List profiles with pagination."""
    with get_db() as conn:
        c = conn.cursor()
        base = "SELECT id, user_id, bio, avatar_url, location, website FROM profiles ORDER BY id DESC"
        sql, params = paginate_query(base, tuple(), page, page_size)
        c.execute(sql, params)
        return fetch_all_dicts(c)


@router.get("/{profile_id}", response_model=ProfileOut, summary="Get profile", operation_id="get_profile")
# PUBLIC_INTERFACE
def get_profile(profile_id: int, _user=Depends(get_current_user)):
    """Get profile by id."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, user_id, bio, avatar_url, location, website FROM profiles WHERE id = ?", (profile_id,))
        row = fetch_one_dict(c)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return row


@router.patch("/{profile_id}", response_model=ProfileOut, summary="Update profile", operation_id="update_profile")
# PUBLIC_INTERFACE
def update_profile(profile_id: int, payload: ProfileUpdate, _user=Depends(get_current_user)):
    """Update profile."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
        if not c.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if payload.bio is not None:
            c.execute("UPDATE profiles SET bio = ? WHERE id = ?", (payload.bio, profile_id))
        if payload.avatar_url is not None:
            c.execute("UPDATE profiles SET avatar_url = ? WHERE id = ?", (payload.avatar_url, profile_id))
        if payload.location is not None:
            c.execute("UPDATE profiles SET location = ? WHERE id = ?", (payload.location, profile_id))
        if payload.website is not None:
            c.execute("UPDATE profiles SET website = ? WHERE id = ?", (payload.website, profile_id))

        c.execute("SELECT id, user_id, bio, avatar_url, location, website FROM profiles WHERE id = ?", (profile_id,))
        return fetch_one_dict(c)


@router.delete("/{profile_id}", summary="Delete profile", operation_id="delete_profile")
# PUBLIC_INTERFACE
def delete_profile(profile_id: int, _user=Depends(get_current_user)):
    """Delete profile."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return {"status": "deleted"}
