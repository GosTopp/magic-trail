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


endpoint = os.getenv("AZURE_INFERENCE_SDK_ENDPOINT")
key = os.getenv("AZURE_INFERENCE_SDK_KEY")
model_name = os.getenv("AZURE_INFERENCE_MODEL", "DeepSeek-R1")
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

start_time = time.time()
response = client.complete(
    messages=[
        SystemMessage(content="你是一个智能助手，你回答问题简洁明了,禁止废话"),
        UserMessage(content="apple 里有几个 p")
    ],
    model=model_name,
    max_tokens=256,
    stream=True
)
print("time:", time.time() - start_time)
for chunk in response:
    print(chunk.choices[0].delta.content)


start_time = time.time()
response = client.complete(
    messages=[
        SystemMessage(content="你是一个智能助手，你回答问题简洁明了,禁止废话"),
        UserMessage(content="apple 里有几个 p")
    ],
    model=model_name,
    max_tokens=256,
    # stream=True
)
print("time:", time.time() - start_time)
content = response.choices[0].message.content
print(content)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def stream_response():
    def generate():
        # 流式响应生成器
        response = client.complete(
            messages=[
                SystemMessage(content="你是一个智能助手，你回答问题简洁明了,禁止废话"),
                UserMessage(content="你好，你是谁")
            ],
            model=model_name,
            max_tokens=256,
            stream=True
        )
        
        for part in response:
            yield part['choices'][0]['message']['content']

    return Response(stream_with_context(generate()), content_type='text/plain;charset=utf-8')

# 非流式响应示例
@app.route('/normal', methods=['POST'])
def normal_response():
    response = client.complete(
        messages=[
            SystemMessage(content="你是一个智能助手，你回答问题简洁明了,禁止废话"),
            UserMessage(content="你好，你是谁")
        ],
        model=model_name,
        max_tokens=256
    )
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
