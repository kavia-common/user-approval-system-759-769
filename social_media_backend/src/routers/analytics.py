from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from src.db.database import get_db, fetch_all_dicts, paginate_query
from src.models.schemas import PostEngagement, UserAnalytics
from src.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/users/{user_id}", response_model=UserAnalytics, summary="User analytics", operation_id="user_analytics")
# PUBLIC_INTERFACE
def get_user_analytics(user_id: int, _user=Depends(get_current_user)):
    """Aggregate analytics for a user."""
    with get_db() as conn:
        c = conn.cursor()
        # ensure user exists
        c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        c.execute(
            """
            SELECT COUNT(*) as total_posts,
                   COALESCE(SUM(likes),0) as total_likes,
                   COALESCE(SUM(comments),0) as total_comments,
                   COALESCE(SUM(shares),0) as total_shares
            FROM posts
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = c.fetchone()
        total_posts = int(row[0] or 0)
        total_likes = int(row[1] or 0)
        total_comments = int(row[2] or 0)
        total_shares = int(row[3] or 0)

        c.execute("SELECT COUNT(*) FROM followers WHERE user_id = ?", (user_id,))
        followers = int(c.fetchone()[0] or 0)

        return {
            "user_id": user_id,
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "followers": followers,
        }


@router.get(
    "/posts",
    response_model=List[PostEngagement],
    summary="Post engagement list",
    operation_id="post_engagement_list",
)
# PUBLIC_INTERFACE
def list_post_engagement(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _user=Depends(get_current_user),
):
    """List posts engagement metrics with pagination."""
    with get_db() as conn:
        c = conn.cursor()
        base = (
            "SELECT id as post_id, likes, comments, shares, "
            "(likes + comments + shares) as engagement "
            "FROM posts "
            "ORDER BY engagement DESC, id DESC"
        )
        sql, params = paginate_query(base, tuple(), page, page_size)
        c.execute(sql, params)
        return fetch_all_dicts(c)
