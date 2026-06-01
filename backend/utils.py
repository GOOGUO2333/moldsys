import jwt
import re
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config

def generate_token(username):
    """Generate JWT token"""
    payload = {
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=Config.JWT_EXPIRATION),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token():
    """Verify JWT token from request header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

# Validation helpers
def validate_username(username):
    """Validate username: 3-20 chars, letters/numbers/underscore"""
    if not username:
        return '用户名不能为空'
    if len(username) < 3 or len(username) > 20:
        return '用户名长度必须为3-20位'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return '用户名只能包含字母、数字和下划线'
    return None

def validate_password(password):
    """Validate password: min 6 chars, must contain letter and number"""
    if not password:
        return '密码不能为空'
    if len(password) < 6:
        return '密码最少6位'
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        return '密码必须包含字母和数字'
    return None

def validate_mold_no(mold_no):
    """Validate mold number: 1-20 chars, letters/numbers only"""
    if not mold_no:
        return '模具编号不能为空'
    if len(mold_no) < 1 or len(mold_no) > 20:
        return '模具编号长度必须为1-20位'
    if not re.match(r'^[a-zA-Z0-9]+$', mold_no):
        return '模具编号只能包含字母和数字'
    return None

def validate_mold_name(name):
    """Validate mold name: 1-50 chars"""
    if not name:
        return '模具名称不能为空'
    if len(name) < 1 or len(name) > 50:
        return '模具名称长度必须为1-50位'
    return None

def validate_positive_int(value, field_name='数值'):
    """Validate positive integer: 1-9999999"""
    try:
        val = int(value)
        if val < 1 or val > 9999999:
            return f'{field_name}必须是1-9,999,999之间的正整数'
        return None
    except (ValueError, TypeError):
        return f'{field_name}必须是正整数'
