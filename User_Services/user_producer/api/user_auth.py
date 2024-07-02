""" Authentication for User Management Service """
from fastapi import Depends, HTTPException, status
from sqlmodel import SQLModel, Session, select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from api.user_model import RefreshTokenData, TokenData, Users, Token

SECRET_KEY = 'ed60732905aeb0315e2f77d05a6cb57a0e408eaf2cb9a77a5a2667931c50d4e0'
ALGORITHYM = 'HS256'
EXPIRY_TIME = 15
REFRESH_EXPIRY_DAYS = 7

pwd_context = CryptContext(schemes="bcrypt")


def create_access_token(data: dict, expiry_time: timedelta | None) -> str:
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHYM)

    return encoded_jwt


def authenticate_user(username: str, password: str, session: Session) -> Users:
    db_user = get_user_from_db(session=session, username=username)
    if not db_user:
        raise HTTPException(
            status_code=401, detail="Invalid username")
    if not verify_password(password=password, password_hash=db_user.password):
        raise HTTPException(
            status_code=401, detail="Invalid password")
    return db_user


def get_user_from_db(session: Session,
                     username: str | None = None,  email: str | None = None) -> Users | None:
    user = session.exec(select(Users).where(
        Users.username == username)).one_or_none()

    if user is None:
        user = session.exec(select(Users).where(
            Users.email == email)).one_or_none()

    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def token_service(user: Users) -> Token:
    """ function to generate access token and refresh token upon successful login """
    expire_time = timedelta(minutes=EXPIRY_TIME)

    access_token = create_access_token({"sub": user.username}, expire_time)

    refresh_expire_time = timedelta(days=REFRESH_EXPIRY_DAYS)

    refresh_token = create_access_token(
        {"sub": user.email}, refresh_expire_time)

    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)


def current_user(token: str, session: Session) -> Users:
    """ function to verify access token """

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
        username: str | None = payload.get("sub")
        if not username:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception

    user = get_user_from_db(session, username=token_data.username)

    if not user:
        raise credential_exception
    return user
