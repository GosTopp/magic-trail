from flask import Flask, request, jsonify
from flask_cors import CORS
from app import app

# 启用 CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://magic-trail.vercel.app", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.debug = True

if __name__ == '__main__':
    app.run() 