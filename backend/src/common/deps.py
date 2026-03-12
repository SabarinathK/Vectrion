from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from src.apps.auth.services import AuthService
from src.common.security import decode_token
from src.platform.db.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Session:
    yield from get_session()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception as exc:
        raise credentials_error from exc

    user = AuthService(db).get_by_id(user_id)
    if not user:
        raise credentials_error
    return user
