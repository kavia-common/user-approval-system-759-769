from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# Basic/Meta

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status string, e.g., 'ok'.")


class Pagination(BaseModel):
    page: int = Field(1, description="Page number, starting at 1.")
    page_size: int = Field(10, description="Items per page (max 100).")


# Auth

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email for demo login.")
    password: str = Field(..., description="Password for demo login (ignored in demo).")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Demo session token.")
    email: EmailStr = Field(..., description="Email associated with token.")


# Users

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Unique user email.")
    name: str = Field(..., description="User full name.")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated name.")
    role: Optional[str] = Field(None, description="Updated role (user/admin).")


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str


# Profiles

class ProfileCreate(BaseModel):
    user_id: int = Field(..., description="User id reference.")
    bio: Optional[str] = Field("", description="Bio text.")
    avatar_url: Optional[str] = Field("", description="Avatar URL.")
    location: Optional[str] = Field("", description="Location.")
    website: Optional[str] = Field("", description="Website.")


class ProfileUpdate(BaseModel):
    bio: Optional[str] = Field(None, description="Bio text.")
    avatar_url: Optional[str] = Field(None, description="Avatar URL.")
    location: Optional[str] = Field(None, description="Location.")
    website: Optional[str] = Field(None, description="Website.")


class ProfileOut(BaseModel):
    id: int
    user_id: int
    bio: str
    avatar_url: str
    location: str
    website: str


# Posts

class PostCreate(BaseModel):
    user_id: int = Field(..., description="Author user id.")
    content: str = Field(..., description="Post content.")


class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated content.")
    likes: Optional[int] = Field(None, description="Updated likes.")
    comments: Optional[int] = Field(None, description="Updated comments.")
    shares: Optional[int] = Field(None, description="Updated shares.")


class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    likes: int
    comments: int
    shares: int


# Analytics

class PostEngagement(BaseModel):
    post_id: int
    likes: int
    comments: int
    shares: int
    engagement: int


class UserAnalytics(BaseModel):
    user_id: int
    total_posts: int
    total_likes: int
    total_comments: int
    total_shares: int
    followers: int


class PlatformAnalytics(BaseModel):
    total_users: int
    total_posts: int
    total_likes: int
    total_comments: int
    total_shares: int
