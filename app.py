from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import time
import requests
 
app = Flask(__name__)
CORS(app)

# 从环境变量读取 Upstash 连接信息
UPSTASH_URL = os.environ.get("STORAGE_KV_REST_API_URL")
UPSTASH_TOKEN = os.environ.get("STORAGE_KV_REST_API_TOKEN")

def exec_redis(cmd, *args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        raise Exception("Upstash 环境变量未配置")
    resp = requests.post(
        f"{UPSTASH_URL}/{cmd}",
        headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
        json=args
    )
    resp.raise_for_status()
    return resp.json()["result"]

@app.route("/api/comments", methods=["GET"])
def get_comments():
    try:
        data = exec_redis("GET", "comments") or "[]"
        comments = json.loads(data)
        return jsonify({"status": "success", "comments": comments})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route("/api/comment", methods=["POST"])
def post_comment():
    try:
        body = request.get_json()
        if not body.get("name") or not body.get("content"):
            return jsonify({"status": "error", "msg": "昵称和内容不能为空"}), 400
        new_cmt = {
            "id": str(int(time.time())),
            "name": body["name"],
            "content": body["content"],
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        old_data = exec_redis("GET", "comments") or "[]"
        comments = json.loads(old_data)
        comments.append(new_cmt)
        exec_redis("SET", "comments", json.dumps(comments))
        return jsonify({"status": "success", "comment": new_cmt})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
