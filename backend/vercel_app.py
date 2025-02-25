import os
import sys

# 添加当前目录到 Python 路径
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

# 然后导入 app
from app import app
