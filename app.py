from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
import requests

app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 修正：读取带前缀的环境变量
UPSTASH_REDIS_URL = os.environ.get("STORAGE_KV_REST_API_URL", "")
UPSTASH_REDIS_TOKEN = os.environ.get("STORAGE_KV_REST_API_TOKEN", "")

def redis_command(command, *args):
    """通过 REST API 执行 Redis 命令"""
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        raise Exception("Upstash Redis 环境变量未配置")
    
    url = f"{UPSTASH_REDIS_URL}/{command}"
    headers = {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
    data = json.dumps(args)
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["result"]

# ...（中间的路由函数保持不变）...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # 修正：生产环境必须关闭 debug 模式
    app.run(host='0.0.0.0', port=port, debug=False)
