import time
import redis
from flask import Flask, jsonify
from app.config import Config

app = Flask(__name__)
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

def create_room():
    room_id = f"room-{int(time.time())}"
    redis_client.publish(f"room:{room_id}", "room_created")
    return room_id

def post_message(room_id, message):
    redis_client.publish(f"room:{room_id}", f"{message}")
