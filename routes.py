from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate, UserUpdate, LoginRequest
from security import hash_password, verify_password, create_access_token, verify_token
from cache_manager import cached
import shutil

router = APIRouter()

def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user:UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already registered")
    new_user = User(name=user.name, email=user.email, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    shutil.rmtree('cache/responses', ignore_errors=True)
    return {"message": "Registered"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"user_id": user.id})
    return {"access_token": token}

@router.get("/users")
@cached
def get_users(db: Session = Depends(get_db), user=Depends(verify_token)):
    users = db.query(User).all()
    return [serialize_user(u) for u in users]

@router.get("/users/{id}")
@cached
def get_users(id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(404, "User not found")
    return serialize_user(u)

@router.put("/users/{id}")
def update_users(id: int, data: UserUpdate, db: Session = Depends(get_db), user=Depends(verify_token)):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(404, "User not found")
    
    if data.name: u.name = data.name
    if data.email: u.email = data.email
    db.commit()
    shutil.rmtree('cache/responses', ignore_errors=True)
    return u

@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(404, "User not found")
    db.delete(u)
    db.commit()
    shutil.rmtree('cache/responses', ignore_errors=True)
    return {"message": "User deleted"}