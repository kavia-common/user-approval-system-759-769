from typing import Optional

from fastapi import Header, HTTPException, status


# PUBLIC_INTERFACE
def get_current_user(authorization: Optional[str] = Header(default=None)):
    """
    PUBLIC_INTERFACE
    Very naive demo auth dependency.

    Accepts an Authorization header in the format:
      Authorization: Bearer demo-token:<email>

    Returns:
        dict: {"email": "<email>"}
    Raises:
        HTTPException 401 if header missing or malformed.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        if not token.startswith("demo-token:"):
            raise ValueError("Invalid token")
        email = token.split("demo-token:", 1)[1]
        if not email:
            raise ValueError("Empty email")
        return {"email": email}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
