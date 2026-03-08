from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time

app = Flask(__name__)
CORS(app)  # 解决跨域

# 评论存储文件（Vercel 上为临时存储，重启后会清空）
COMMENT_FILE = "comments.json"

# 初始化评论文件
def init_comments():
    if not os.path.exists(COMMENT_FILE):
        with open(COMMENT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# 获取所有评论
@app.route('/api/comments', methods=['GET'])
def get_comments():
    init_comments()
    with open(COMMENT_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    comments.sort(key=lambda x: x["time"], reverse=True)
    return jsonify({"status": "success", "comments": comments})

# 提交评论
@app.route('/api/comment', methods=['POST'])
def add_comment():
    init_comments()
    data = request.get_json()
    if not data or not data.get("name") or not data.get("content"):
        return jsonify({"status": "error", "message": "Name and content are required!"}), 400
    
    new_comment = {
        "id": str(int(time.time())),
        "name": data["name"],
        "content": data["content"],
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    with open(COMMENT_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    comments.append(new_comment)
    with open(COMMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    return jsonify({"status": "success", "message": "Comment submitted successfully!", "comment": new_comment})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
