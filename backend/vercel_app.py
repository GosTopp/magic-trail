try:
    from app import app
except ImportError:
    from .app import app

# Vercel需要这个来作为入口点 

# 确保实例可被 Vercel 调用 