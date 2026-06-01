from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": ["*"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Authorization", "Content-Type"]}})

# Register blueprints
from routes.auth import auth_bp
from routes.molds import molds_bp
app.register_blueprint(auth_bp)
app.register_blueprint(molds_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'code': 200, 'message': 'OK'})

# Serve static files for local dev (not in Docker)
dist_path = os.path.join(os.path.dirname(__file__), 'dist')
is_docker = os.environ.get('DOCKER_ENV') == '1'

if os.path.exists(dist_path) and not is_docker:
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(dist_path, 'assets'), filename)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path.startswith('api/'):
            return jsonify({'code': 404, 'message': '接口不存在'}), 404
        fp = os.path.join(dist_path, path)
        if path and os.path.exists(fp) and os.path.isfile(fp):
            return send_from_directory(dist_path, path)
        return send_from_directory(dist_path, 'index.html')

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 404, 'message': '接口不存在'}), 404
    if is_docker and os.path.exists(dist_path):
        return send_from_directory(dist_path, 'index.html')
    return jsonify({'code': 404, 'message': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
