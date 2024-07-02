from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from api.user_model import Token, Users, Register_User
from typing import Annotated
from api.user_model import Users
from common_files.database import get_session
import api.user_auth as auth

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register")
async def regiser_user(new_user: Annotated[Register_User, Depends()],
                       session: Annotated[Session, Depends(get_session)]):
    db_user = auth.get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(
            status_code=409, detail="User with these credentials already exists")

    user = Users(username=new_user.username,
                 email=new_user.email,
                 password=auth.hash_password(new_user.password))

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f""" User with {user.username} successfully registered """}


@router.post('/login', response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Annotated[Session, Depends(get_session)]) -> Token:
    user: Users = auth.authenticate_user(
        form_data.username, form_data.password, session)
    return auth.token_service(user)


@router.get('/profile', response_model=Users)
async def user_profile(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]) -> Users:
    return auth.current_user(token, session)


@router.get("/users", response_model=list[Users])
async def get_users(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    return session.exec(select(Users)).all()
