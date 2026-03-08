from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有跨域，方便测试

# 读取 Upstash 注入的环境变量（带前缀）
UPSTASH_REDIS_URL = os.environ.get("STORAGE_KV_REST_API_URL", "")
UPSTASH_REDIS_TOKEN = os.environ.get("STORAGE_KV_REST_API_TOKEN", "")

def redis_command(command, *args):
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        raise Exception("Upstash Redis 环境变量未配置")
    
    url = f"{UPSTASH_REDIS_URL}/{command}"
    headers = {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
    data = json.dumps(args)
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["result"]

@app.route('/api/comments', methods=['GET'])
def get_comments():
    try:
        comments_json = redis_command("GET", "comments") or "[]"
        comments = json.loads(comments_json)
        comments.sort(key=lambda x: x["time"], reverse=True)
        return jsonify({"status": "success", "comments": comments})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("content"):
        return jsonify({"status": "error", "message": "姓名和内容不能为空"}), 400
    
    try:
        new_comment = {
            "id": str(int(time.time())),
            "name": data["name"].strip(),
            "content": data["content"].strip(),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        comments_json = redis_command("GET", "comments") or "[]"
        comments = json.loads(comments_json)
        comments.append(new_comment)
        
        redis_command("SET", "comments", json.dumps(comments, ensure_ascii=False))
        return jsonify({"status": "success", "comment": new_comment})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 清空评论（测试用）
@app.route('/api/comments/clear', methods=['POST'])
def clear_comments():
    try:
        redis_command("SET", "comments", json.dumps([]))
        return jsonify({"status": "success", "message": "所有评论已清空"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # 生产环境必须关闭 debug
