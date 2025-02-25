from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# 添加后端目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 导入 Flask 应用
from app import app

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 使用 Flask 应用处理请求
        with app.test_request_context(
            method='POST',
            input_stream=post_data,
            content_type=self.headers.get('Content-Type')
        ):
            response = app.full_dispatch_request()
            
        self.send_response(response.status_code)
        for header, value in response.headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.get_data()) 