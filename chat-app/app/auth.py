from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

# User model (simplified)
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

# Login endpoint (simplified)
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    # Validate user (real DB would be here)
    user = User(email, password)
    
    # Generate JWT token
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)
