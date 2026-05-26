from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List, Dict, Optional
import sqlite3
import asyncio
from fastapi import WebSocket
from websocket_manager import WebSocketManager  

SECRET_KEY = "your_secret_key_here"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(room_id) REFERENCES rooms(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserBase(BaseModel):
    email: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    content: str
    room_id: int
    user_id: int

class Room(BaseModel):
    name: str
class WebSocketManager:
    def __init__(self):
        self.connections = {}
    
    def add_connection(self, websocket, room_id):
        self.connections[room_id] = websocket
    
    def remove_connection(self, room_id):
        if room_id in self.connections:
            del self.connections[room_id]
    
    def broadcast(self, room_id, message):
        if room_id in self.connections:
            self.connections[room_id].send_json(message)


def get_user_by_email(email: str):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

app = FastAPI()
websocket_manager = WebSocketManager()

@app.post("/register")
async def register_user(user: UserCreate):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if c.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (user.email, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(user: UserCreate):
    user_data = get_user_by_email(user.email)
    if not user_data:
        raise HTTPException(status_code=400, detail="Email not found")
    
    if not pwd_context.verify(user.password, user_data[1]):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user_data[0], "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/rooms")
async def get_rooms():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms = [{"id": r[0], "name": r[1]} for r in c.fetchall()]
    conn.close()
    return rooms

@app.post("/rooms")
async def create_room(room: Room):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO rooms (name) VALUES (?)", (room.name,))
    room_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": room_id, "name": room.name}

@app.websocket("/rooms/{room_id}/chat")
async def chat_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            conn = sqlite3.connect("chat.db")
            c = conn.cursor()
            c.execute("INSERT INTO messages (room_id, content) VALUES (?, ?)",(room_id, content))
            conn.commit()
            conn.close()
            for user_id in websocket_manager.rooms.get(room_id, []):
                await websocket_manager.send_json(user_id, {"content": message})
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.remove_websocket(websocket)


if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
