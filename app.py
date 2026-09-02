"""
智能制造知识库问答系统 - 后端服务
基于 Flask 的 RESTful API，集成 BM25 + Faiss 多路召回
"""
from flask_cors import CORS
import json
import pickle
import time
import tempfile
import shutil
import jieba
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

from database import init_db, insert_log, get_history, get_stats

import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"


def load_faiss_index_safe(index_path):
    """
    安全加载Faiss索引，解决Windows中文路径无法读取的问题。
    通过复制到系统临时目录（纯英文路径）后加载。
    """
    try:
        return faiss.read_index(index_path)
    except Exception:
        # 中文路径加载失败，使用临时英文路径
        tmp_path = os.path.join(tempfile.gettempdir(), 'qa_index_tmp.faiss')
        shutil.copy2(index_path, tmp_path)
        index = faiss.read_index(tmp_path)
        os.remove(tmp_path)
        return index


app = Flask(__name__)
CORS(app)

# 初始化数据库
init_db()

# 加载索引和元数据
print("加载索引...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
index = load_faiss_index_safe('data/qa_index.faiss')
with open('data/bm25.pkl', 'rb') as f:
    bm25 = pickle.load(f)
with open('data/qa_meta.pkl', 'rb') as f:
    meta = pickle.load(f)
questions = meta['questions']
answers = meta['answers']
print(f"✅ 索引加载完成，共 {len(questions)} 条问答对")


def retrieve(query, top_k=5):
    """
    多路召回检索：BM25全文检索 + Faiss向量检索 + 融合排序
    """
    start_time = time.time()

    # 向量检索
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)
    scores_vec, idx_vec = index.search(query_vec, top_k)

    # BM25 检索
    tokenized_query = list(jieba.cut(query))
    scores_bm25 = bm25.get_scores(tokenized_query)
    top_bm25 = np.argsort(scores_bm25)[-top_k:][::-1]

    # 融合排序（RRF思想：按排名给分）
    candidates = {}
    for i, idx in enumerate(idx_vec[0]):
        candidates[idx] = candidates.get(idx, 0) + (top_k - i) * 0.5
    for i, idx in enumerate(top_bm25):
        candidates[idx] = candidates.get(idx, 0) + (top_k - i) * 0.5

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    result_indices = [idx for idx, _ in sorted_candidates[:top_k]]

    results = []
    for idx in result_indices:
        results.append({
            'question': questions[idx],
            'answer': answers[idx],
            'score': float(candidates[idx])
        })

    latency_ms = int((time.time() - start_time) * 1000)
    return results, latency_ms


@app.route('/ask', methods=['POST'])
def ask():
    """问答接口：接收自然语言问题，返回检索结果"""
    data = request.get_json()
    query = data.get('question', '')
    if not query:
        return jsonify({'error': '缺少问题'}), 400

    results, latency_ms = retrieve(query)

    # 记录问答日志到数据库
    top_result = results[0] if results else None
    insert_log(
        question=query,
        top_question=top_result['question'] if top_result else '',
        top_answer=top_result['answer'] if top_result else '',
        score=top_result['score'] if top_result else 0,
        latency_ms=latency_ms
    )

    return jsonify({
        'question': query,
        'results': results,
        'latency_ms': latency_ms
    })


@app.route('/stats', methods=['GET'])
def stats():
    """统计接口：返回系统统计信息"""
    s = get_stats()
    s['total_knowledge'] = len(questions)
    return jsonify(s)


@app.route('/history', methods=['GET'])
def history():
    """历史记录接口：返回最近的问答日志"""
    limit = request.args.get('limit', 20, type=int)
    logs = get_history(limit)
    return jsonify({'logs': logs, 'count': len(logs)})


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'knowledge_count': len(questions)})


if __name__ == '__main__':
    print("🚀 智能制造知识库问答系统启动中...")
    print("📡 访问地址: http://127.0.0.1:5000")
    print("📄 前端页面: 直接用浏览器打开 index.html")
    app.run(debug=False, host='0.0.0.0', port=5000)
