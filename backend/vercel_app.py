from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建新的 Flask 应用
app = Flask(__name__)

# 启用 CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://magic-trail.vercel.app", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 导入路由
try:
    from backend.app import routes
    # 如果 app.py 中有路由函数，可以手动注册
    # 例如: app.route('/api/endpoint')(routes.endpoint_function)
except ImportError:
    print("无法导入路由")

app.debug = True

# 添加一个测试路由
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API 工作正常!"})

if __name__ == '__main__':
    app.run() 