from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import yaml
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载景点信息和提示词
try:
    attractions_path = os.path.join(project_root, 'public', 'attractions', 'all_attractions.json')
    with open(attractions_path, 'r', encoding='utf-8') as f:
        attractions_info = json.load(f)

    prompt_path = os.path.join(project_root, 'public', 'prompt.yml')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    _travel_prompt = prompts['travel_guide_prompt']
except Exception as e:
    print(f"Error loading files: {str(e)}")
    attractions_info = []
    _travel_prompt = ""

# 加载环境变量
load_dotenv()

endpoint = os.environ.get("AZURE_INFERENCE_SDK_ENDPOINT")
key = os.environ.get("AZURE_INFERENCE_SDK_KEY")
model_name = os.environ.get("AZURE_INFERENCE_MODEL", "DeepSeek-R1")

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

@app.route('/api/travel_guide', methods=['POST', 'OPTIONS'])
def travel_guide():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        data = request.get_json(force=True)
        user_input = data.get("input-guide", "")
        
        if not user_input:
            return jsonify({"error": "输入不能为空"}), 400

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
            try:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        data = json.dumps({'content': content}, ensure_ascii=False)
                        yield f"data: {data}\n\n"
            except Exception as e:
                print(f"Streaming error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            }
        )

    except Exception as e:
        print(f"Error in travel_guide: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

# Vercel 需要的处理函数
def handler(request, context):
    return app(request) 