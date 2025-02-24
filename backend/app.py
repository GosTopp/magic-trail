from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

import json
import os
from typing import List, Dict
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time
import codecs
import yaml

# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 修改文件读取路径
try:
    # 读取景点信息
    attractions_path = os.path.join(project_root, 'public', 'attractions', 'all_attractions.json')
    with open(attractions_path, 'r', encoding='utf-8') as f:
        attractions_info = json.load(f)

    # 读取提示词
    prompt_path = os.path.join(project_root, 'public', 'prompt.yml')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    _travel_prompt = prompts['travel_guide_prompt']
except Exception as e:
    print(f"Error loading files: {str(e)}")
    attractions_info = []
    _travel_prompt = ""

# 加载 .env 文件中的环境变量
load_dotenv()

app = Flask(__name__)
app.logger.setLevel('DEBUG')  # 设置日志级别为 DEBUG

# 最简单的 CORS 配置
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 在生产环境中应该设置具体的域名
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"]
    }
})

endpoint = os.getenv("AZURE_INFERENCE_SDK_ENDPOINT")
key = os.getenv("AZURE_INFERENCE_SDK_KEY")
model_name = os.getenv("AZURE_INFERENCE_MODEL", "DeepSeek-R1")
# model_name = os.getenv("AZURE_INFERENCE_MODEL", "gpt-4o-mini")
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# 添加一个测试路由
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

@app.route('/api/travel_guide', methods=['GET', 'POST', 'OPTIONS'])
def travel_guide():
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        if request.method == 'POST':
            app.logger.info("Received POST request")
            data = request.get_json(force=True)
            user_input = data.get("input-guide", "")
            
            if not user_input:
                return jsonify({"error": "输入不能为空"}), 400

            # 检查环境变量
            if not endpoint or not key:
                return jsonify({"error": "API 配置错误"}), 500

            # 记录更多日志
            app.logger.info(f"Processing request with input length: {len(user_input)}")
            
            app.logger.info("Calling Azure AI Inference API")
            
            # 将用户输入与景点信息结合
            formatted_prompt = _travel_prompt.format(
                user_input=user_input,
                attractions=attractions_info
            )
            
            response = client.complete(
                messages=[
                    SystemMessage(content="根据用户需求和上海迪士尼官方信息，为用户定制游玩攻略"),
                    UserMessage(content=formatted_prompt)
                ],
                model=model_name,
                max_tokens=2048,
                stream=True
            )

            def generate():
                for chunk in response:
                    try:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            # content = content.decode('utf-8', errors='ignore')
                            # content = content.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                            data = json.dumps({'content': content}, ensure_ascii=False)
                            yield f"data: {data}\n\n"
                            time.sleep(0.01)
                    except Exception as e:
                        app.logger.error(f"处理数据流时出错: {str(e)}")
                        continue

            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Content-Type': 'text/event-stream; charset=utf-8'
                }
            )
    
    except Exception as e:
        app.logger.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": f"处理请求时发生错误: {str(e)}"}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    app.logger.error(f"方法不允许: {request.method} {request.path}")
    return jsonify({
        "error": "不支持的请求方法",
        "message": f"该接口不支持 {request.method} 方法"
    }), 405

@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"发生错误: {str(error)}", exc_info=True)
    return jsonify({
        "error": "服务器内部错误",
        "message": str(error)
    }), 500

if __name__ == '__main__':
    # 设置日志级别为 DEBUG
    app.logger.setLevel('DEBUG')
    app.run(debug=True, host='0.0.0.0', port=5001)
    
