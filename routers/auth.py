from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


@router.post(
    "/register",
    status_code=201,
    response_model=UserResponse,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user