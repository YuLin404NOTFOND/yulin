"""
SQLite 数据库模块
负责问答日志的存储、查询和统计
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/qa_system.db'


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，创建表结构"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            top_question TEXT,
            top_answer TEXT,
            score REAL,
            latency_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")


def insert_log(question, top_question, top_answer, score, latency_ms):
    """插入一条问答日志"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO qa_log (question, top_question, top_answer, score, latency_ms)
        VALUES (?, ?, ?, ?, ?)
    ''', (question, top_question, top_answer, score, latency_ms))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def get_history(limit=20):
    """获取历史问答记录，按时间倒序"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, question, top_question, top_answer, score, latency_ms, created_at
        FROM qa_log
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """获取系统统计信息"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM qa_log')
    total_logs = cursor.fetchone()['total']

    cursor.execute('SELECT AVG(latency_ms) as avg_latency FROM qa_log WHERE latency_ms > 0')
    avg_row = cursor.fetchone()
    avg_latency = round(avg_row['avg_latency'], 1) if avg_row['avg_latency'] else 0

    cursor.execute('''
        SELECT question, COUNT(*) as cnt
        FROM qa_log
        GROUP BY question
        ORDER BY cnt DESC
        LIMIT 5
    ''')
    hot_questions = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        'total_logs': total_logs,
        'avg_latency_ms': avg_latency,
        'hot_questions': hot_questions
    }


if __name__ == '__main__':
    init_db()
    print("数据库表结构创建成功")
