import json
import pickle
import jieba
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

app = Flask(__name__)

# 加载索引和元数据
print("加载索引...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # 使用相同模型
index = faiss.read_index('data/qa_index.faiss')
with open('data/bm25.pkl', 'rb') as f:
    bm25 = pickle.load(f)
with open('data/qa_meta.pkl', 'rb') as f:
    meta = pickle.load(f)
questions = meta['questions']
answers = meta['answers']

def retrieve(query, top_k=5):
    # 向量检索
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)
    scores_vec, idx_vec = index.search(query_vec, top_k)

    # BM25 检索
    tokenized_query = list(jieba.cut(query))
    scores_bm25 = bm25.get_scores(tokenized_query)
    top_bm25 = np.argsort(scores_bm25)[-top_k:][::-1]

    # 融合排序
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
    return results

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('question', '')
    if not query:
        return jsonify({'error': '缺少问题'}), 400
    results = retrieve(query)
    return jsonify({'question': query, 'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)