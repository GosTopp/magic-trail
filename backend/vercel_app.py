from flask import Flask, request, jsonify
from app import app

app.debug = True

if __name__ == '__main__':
    app.run() 