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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # 使用 Flask 应用处理请求
            with app.test_request_context(
                path='/api/travel_guide',
                method='POST',
                input_stream=post_data,
                content_type=self.headers.get('Content-Type', 'application/json'),
                headers=dict(self.headers)
            ):
                response = app.full_dispatch_request()
            
            # 设置响应头
            self.send_response(response.status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('X-Accel-Buffering', 'no')
            
            # 添加响应头
            for header, value in response.headers.items():
                if header.lower() not in ['content-type', 'content-length']:
                    self.send_header(header, value)
            
            self.end_headers()
            
            # 写入响应数据
            response_data = response.get_data()
            if response_data:
                self.wfile.write(response_data)
                self.wfile.flush()
                
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode()) 