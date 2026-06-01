from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import get_db_connection
from utils import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    # Basic validation
    if not username:
        return jsonify({'code': 400, 'message': '请输入用户名'}), 400
    if not password:
        return jsonify({'code': 400, 'message': '请输入密码'}), 400
    
    # Check credentials
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
        
        token = generate_token(username)
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token,
                'username': user['username']
            }
        })
    finally:
        conn.close()
