from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.db.database import get_db, fetch_one_dict, fetch_all_dicts, paginate_query
from src.models.schemas import PostCreate, PostOut, PostUpdate
from src.utils.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut, summary="Create post", operation_id="create_post")
# PUBLIC_INTERFACE
def create_post(payload: PostCreate, _user=Depends(get_current_user)):
    """Create a new post."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE id = ?", (payload.user_id,))
        if not c.fetchone():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")

        c.execute(
            "INSERT INTO posts (user_id, content, likes, comments, shares) VALUES (?, ?, 0, 0, 0)",
            (payload.user_id, payload.content),
        )
        pid = c.lastrowid
        c.execute("SELECT id, user_id, content, likes, comments, shares FROM posts WHERE id = ?", (pid,))
        return fetch_one_dict(c)


@router.get("", response_model=List[PostOut], summary="List posts", operation_id="list_posts")
# PUBLIC_INTERFACE
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _user=Depends(get_current_user),
):
    """List posts with pagination."""
    with get_db() as conn:
        c = conn.cursor()
        base = "SELECT id, user_id, content, likes, comments, shares FROM posts ORDER BY id DESC"
        sql, params = paginate_query(base, tuple(), page, page_size)
        c.execute(sql, params)
        return fetch_all_dicts(c)


@router.get("/{post_id}", response_model=PostOut, summary="Get post", operation_id="get_post")
# PUBLIC_INTERFACE
def get_post(post_id: int, _user=Depends(get_current_user)):
    """Get post by id."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, user_id, content, likes, comments, shares FROM posts WHERE id = ?", (post_id,))
        row = fetch_one_dict(c)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return row


@router.patch("/{post_id}", response_model=PostOut, summary="Update post", operation_id="update_post")
# PUBLIC_INTERFACE
def update_post(post_id: int, payload: PostUpdate, _user=Depends(get_current_user)):
    """Update post content or engagement counts."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if not c.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if payload.content is not None:
            c.execute("UPDATE posts SET content = ? WHERE id = ?", (payload.content, post_id))
        if payload.likes is not None:
            c.execute("UPDATE posts SET likes = ? WHERE id = ?", (payload.likes, post_id))
        if payload.comments is not None:
            c.execute("UPDATE posts SET comments = ? WHERE id = ?", (payload.comments, post_id))
        if payload.shares is not None:
            c.execute("UPDATE posts SET shares = ? WHERE id = ?", (payload.shares, post_id))

        c.execute("SELECT id, user_id, content, likes, comments, shares FROM posts WHERE id = ?", (post_id,))
        return fetch_one_dict(c)


@router.delete("/{post_id}", summary="Delete post", operation_id="delete_post")
# PUBLIC_INTERFACE
def delete_post(post_id: int, _user=Depends(get_current_user)):
    """Delete post by id."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return {"status": "deleted"}
