import json
import pickle
import jieba
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

print("加载预处理数据...")
with open('data/processed_qa.json', 'r', encoding='utf-8') as f:
    qa_pairs = json.load(f)

questions = [item['question'] for item in qa_pairs]
answers = [item['answer'] for item in qa_pairs]

# 1. 构建 BM25 索引（中文分词）
print("构建 BM25 索引...")
tokenized_questions = [list(jieba.cut(q)) for q in questions]
bm25 = BM25Okapi(tokenized_questions)

# 2. 构建向量索引（Sentence-BERT）
print("加载 Sentence-BERT 模型...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("生成句子向量...")
embeddings = model.encode(questions, convert_to_numpy=True)
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
faiss.normalize_L2(embeddings)
index.add(embeddings)

# 保存索引和辅助数据
print("保存索引...")
faiss.write_index(index, 'data/qa_index.faiss')
with open('data/bm25.pkl', 'wb') as f:
    pickle.dump(bm25, f)
with open('data/qa_meta.pkl', 'wb') as f:
    pickle.dump({'questions': questions, 'answers': answers}, f)

print(f"✅ 索引构建完成！共 {len(qa_pairs)} 条问答对。")