from repositories.database import db
from passlib.context import CryptContext
from fastapi import HTTPException
from utils.jwt_handler import create_access_token
from bson.objectid import ObjectId
from utils.jwt_handler import decode_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]

async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

async def register_user(data):
    existing = await get_user_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    hashed = pwd_context.hash(data.password)
    new_user = {
        "name": data.name,
        "email": data.email,
        "password": hashed
    }
    await users_collection.insert_one(new_user)
    return {"msg": "Đăng ký thành công"}

async def login_user(data):
    user = await get_user_by_email(data.email)
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Thông tin đăng nhập không chính xác")

    token = create_access_token({"sub": user["email"]})
    return {
        "token": token,
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }

async def verify_user(token: str):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")
    email = payload.get("sub")
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return {
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }
