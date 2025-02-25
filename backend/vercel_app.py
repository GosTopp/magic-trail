from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import openai
import flask

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建新的 Flask 应用
app = Flask(__name__)

# 修改 CORS 配置，允许所有来源
CORS(app, resources={
    r"/*": {
        "origins": "*",  # 允许所有来源
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 确保正确设置了 OpenAI API 密钥
openai.api_key = os.environ.get("OPENAI_API_KEY")

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

# 添加 travel_guide 路由
@app.route('/api/travel_guide', methods=['GET', 'POST', 'OPTIONS'])
def travel_guide():
    if request.method == 'OPTIONS':
        print("Handling OPTIONS request")
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        if request.method == 'POST':
            print("=== 开始处理新的旅游攻略请求 ===")
            print(f"请求头: {dict(request.headers)}")
            
            data = request.get_json(force=True)
            user_input = data.get("input-guide", "")
            
            print(f"用户输入数据: {user_input}")
            
            if not user_input:
                print("收到空输入")
                return jsonify({"error": "输入不能为空"}), 400

            # 检查环境变量
            endpoint = os.environ.get("AZURE_INFERENCE_SDK_ENDPOINT")
            key = os.environ.get("AZURE_INFERENCE_SDK_KEY")
            model_name = os.environ.get("AZURE_INFERENCE_MODEL", "DeepSeek-R1")
            
            if not endpoint or not key:
                print("API配置缺失: endpoint或key未设置")
                return jsonify({"error": "API 配置错误"}), 500

            # 简化版响应，用于测试
            return jsonify({
                "content": "# 测试响应\n\n这是一个测试响应，用于验证API是否正常工作。\n\n如果您看到这条消息，说明API已成功连接。"
            })
            
    except Exception as e:
        print(f"处理请求时发生错误: {str(e)}")
        import traceback
        print(f"详细错误追踪:\n{traceback.format_exc()}")
        return jsonify({"error": f"处理请求时发生错误: {str(e)}"}), 500

@app.route('/api/plan', methods=['POST'])
def plan_trip():
    try:
        data = request.json
        # 处理逻辑...
        # 确保这里有适当的错误处理和日志记录
        
        # 返回响应...
        return jsonify({"plan": result})
    except Exception as e:
        print(f"Error: {str(e)}")  # 添加日志记录
        return jsonify({"error": str(e)}), 500

# 添加一个简单的健康检查端点
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/api/debug', methods=['GET'])
def debug():
    """调试端点，返回环境信息"""
    return jsonify({
        "status": "ok",
        "env": {
            "has_azure_endpoint": bool(os.environ.get("AZURE_INFERENCE_SDK_ENDPOINT")),
            "has_azure_key": bool(os.environ.get("AZURE_INFERENCE_SDK_KEY")),
            "model_name": os.environ.get("AZURE_INFERENCE_MODEL", "未设置"),
            "python_version": sys.version,
            "flask_version": flask.__version__
        }
    })

if __name__ == '__main__':
    app.run() 