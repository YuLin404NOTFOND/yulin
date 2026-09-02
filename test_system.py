"""
智能制造知识库问答系统 - 自动化测试
覆盖：数据预处理、索引构建、数据库、API接口、检索功能
运行方式: python test_system.py
"""
import unittest
import json
import os
import sys
import tempfile
import sqlite3

# 测试配置
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')


class TestDataPreprocessing(unittest.TestCase):
    """测试数据预处理模块"""

    def test_processed_file_exists(self):
        """测试预处理后的问答对文件是否存在"""
        path = os.path.join(DATA_DIR, 'processed_qa.json')
        self.assertTrue(os.path.exists(path), f"预处理文件不存在: {path}")

    def test_processed_file_valid_json(self):
        """测试预处理文件是否为有效JSON"""
        path = os.path.join(DATA_DIR, 'processed_qa.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, list, "预处理数据应为列表")

    def test_qa_pair_structure(self):
        """测试每条问答对的结构是否正确"""
        path = os.path.join(DATA_DIR, 'processed_qa.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertGreater(len(data), 0, "问答对数量应大于0")
        for item in data[:10]:  # 抽样检查前10条
            self.assertIn('question', item, "缺少question字段")
            self.assertIn('answer', item, "缺少answer字段")
            self.assertIsInstance(item['question'], str)
            self.assertIsInstance(item['answer'], str)
            self.assertGreater(len(item['question'].strip()), 0, "问题不能为空")
            self.assertGreater(len(item['answer'].strip()), 0, "答案不能为空")

    def test_qa_count_reasonable(self):
        """测试问答对数量是否合理（PANDAX数据集约1860条）"""
        path = os.path.join(DATA_DIR, 'processed_qa.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertGreaterEqual(len(data), 1000, f"问答对数量过少: {len(data)}")
        self.assertLessEqual(len(data), 5000, f"问答对数量异常: {len(data)}")


class TestIndexFiles(unittest.TestCase):
    """测试索引文件"""

    def test_faiss_index_exists(self):
        """测试Faiss向量索引文件是否存在"""
        path = os.path.join(DATA_DIR, 'qa_index.faiss')
        self.assertTrue(os.path.exists(path), f"Faiss索引文件不存在: {path}")
        self.assertGreater(os.path.getsize(path), 0, "Faiss索引文件为空")

    def test_bm25_index_exists(self):
        """测试BM25索引文件是否存在"""
        path = os.path.join(DATA_DIR, 'bm25.pkl')
        self.assertTrue(os.path.exists(path), f"BM25索引文件不存在: {path}")
        self.assertGreater(os.path.getsize(path), 0, "BM25索引文件为空")

    def test_meta_file_exists(self):
        """测试元数据文件是否存在"""
        path = os.path.join(DATA_DIR, 'qa_meta.pkl')
        self.assertTrue(os.path.exists(path), f"元数据文件不存在: {path}")
        self.assertGreater(os.path.getsize(path), 0, "元数据文件为空")

    def test_meta_structure(self):
        """测试元数据结构是否正确"""
        import pickle
        path = os.path.join(DATA_DIR, 'qa_meta.pkl')
        with open(path, 'rb') as f:
            meta = pickle.load(f)
        self.assertIn('questions', meta, "元数据缺少questions")
        self.assertIn('answers', meta, "元数据缺少answers")
        self.assertEqual(len(meta['questions']), len(meta['answers']),
                         "问题和答案数量不一致")


class TestDatabase(unittest.TestCase):
    """测试SQLite数据库模块"""

    def setUp(self):
        """每个测试前创建临时数据库"""
        self.tmp_db = tempfile.mktemp(suffix='.db')
        # 临时替换数据库路径
        import database
        self.original_path = database.DB_PATH
        database.DB_PATH = self.tmp_db

    def tearDown(self):
        """测试后清理"""
        import database
        database.DB_PATH = self.original_path
        if os.path.exists(self.tmp_db):
            os.remove(self.tmp_db)

    def test_init_db_creates_table(self):
        """测试数据库初始化是否创建表"""
        import database
        database.init_db()
        self.assertTrue(os.path.exists(self.tmp_db), "数据库文件未创建")
        conn = sqlite3.connect(self.tmp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='qa_log'")
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result, "qa_log表未创建")

    def test_insert_and_query_log(self):
        """测试插入和查询日志"""
        import database
        database.init_db()
        log_id = database.insert_log(
            question="测试问题",
            top_question="匹配问题",
            top_answer="测试答案",
            score=3.5,
            latency_ms=120
        )
        self.assertIsInstance(log_id, int, "返回的日志ID应为整数")
        self.assertGreater(log_id, 0, "日志ID应大于0")

        history = database.get_history(limit=10)
        self.assertEqual(len(history), 1, "历史记录数量应为1")
        self.assertEqual(history[0]['question'], '测试问题')
        self.assertEqual(history[0]['top_answer'], '测试答案')

    def test_stats(self):
        """测试统计功能"""
        import database
        database.init_db()
        database.insert_log("问题A", "匹配A", "答案A", 2.0, 100)
        database.insert_log("问题B", "匹配B", "答案B", 3.0, 200)

        stats = database.get_stats()
        self.assertEqual(stats['total_logs'], 2)
        self.assertEqual(stats['avg_latency_ms'], 150.0)
        self.assertEqual(len(stats['hot_questions']), 2)


class TestRetrievalModule(unittest.TestCase):
    """测试检索模块（需要加载索引，较慢）"""

    @classmethod
    def setUpClass(cls):
        """所有测试前加载一次索引"""
        try:
            import pickle
            import jieba
            import numpy as np
            from sentence_transformers import SentenceTransformer
            import faiss
            from rank_bm25 import BM25Okapi

            cls.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            cls.index = faiss.read_index(os.path.join(DATA_DIR, 'qa_index.faiss'))
            with open(os.path.join(DATA_DIR, 'bm25.pkl'), 'rb') as f:
                cls.bm25 = pickle.load(f)
            with open(os.path.join(DATA_DIR, 'qa_meta.pkl'), 'rb') as f:
                meta = pickle.load(f)
            cls.questions = meta['questions']
            cls.answers = meta['answers']
            cls.modules_loaded = True
        except Exception as e:
            print(f"\n⚠️  索引加载失败，跳过检索测试: {e}")
            cls.modules_loaded = False

    def test_vector_search_returns_results(self):
        """测试向量检索是否返回结果"""
        if not self.modules_loaded:
            self.skipTest("索引未加载")
        query_vec = self.model.encode(['冷却系统'], convert_to_numpy=True)
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, 5)
        self.assertEqual(len(indices[0]), 5, "应返回5个结果")
        self.assertGreater(len(self.questions[indices[0][0]]), 0, "返回的问题不应为空")

    def test_bm25_search_returns_results(self):
        """测试BM25检索是否返回结果"""
        if not self.modules_loaded:
            self.skipTest("索引未加载")
        import numpy as np
        tokenized = list(jieba.cut('冷却系统有哪些类型'))
        scores = self.bm25.get_scores(tokenized)
        self.assertEqual(len(scores), len(self.questions), "BM25得分数量应与问答对数量一致")
        top_idx = np.argmax(scores)
        self.assertGreater(scores[top_idx], 0, "最高得分应大于0")

    def test_fusion_ranking(self):
        """测试融合排序逻辑"""
        if not self.modules_loaded:
            self.skipTest("索引未")
        import numpy as np
        top_k = 5
        query = '冷却系统'

        # 向量检索
        query_vec = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vec)
        _, idx_vec = self.index.search(query_vec, top_k)

        # BM25检索
        tokenized = list(jieba.cut(query))
        scores_bm25 = self.bm25.get_scores(tokenized)
        top_bm25 = np.argsort(scores_bm25)[-top_k:][::-1]

        # 融合
        candidates = {}
        for i, idx in enumerate(idx_vec[0]):
            candidates[idx] = candidates.get(idx, 0) + (top_k - i) * 0.5
        for i, idx in enumerate(top_bm25):
            candidates[idx] = candidates.get(idx, 0) + (top_k - i) * 0.5

        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        self.assertGreater(len(sorted_candidates), 0, "融合结果不应为空")
        self.assertLessEqual(len(sorted_candidates), top_k * 2, "融合结果数量不应超过2*top_k")


class TestAPIInterface(unittest.TestCase):
    """测试API接口定义（不启动服务器，仅检查路由注册）"""

    def test_flask_app_exists(self):
        """测试Flask应用是否存在"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", os.path.join(TEST_DIR, 'app.py'))
        self.assertIsNotNone(spec, "app.py模块加载失败")

    def test_app_has_required_routes(self):
        """测试app.py是否包含必要的路由"""
        with open(os.path.join(TEST_DIR, 'app.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("@app.route('/ask'", content, "缺少/ask路由")
        self.assertIn("@app.route('/stats'", content, "缺少/stats路由")
        self.assertIn("@app.route('/history'", content, "缺少/history路由")
        self.assertIn("@app.route('/health'", content, "缺少/health路由")

    def test_database_integration(self):
        """测试app.py是否集成了数据库模块"""
        with open(os.path.join(TEST_DIR, 'app.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('from database import', content, "未导入database模块")
        self.assertIn('insert_log', content, "未调用insert_log记录日志")


class TestProjectStructure(unittest.TestCase):
    """测试项目结构完整性"""

    def test_required_files_exist(self):
        """测试必要文件是否存在"""
        required_files = [
            'app.py',
            'preprocess.py',
            'build_index.py',
            'database.py',
            'index.html',
            'README.md',
            'requirements.txt',
            '选题说明.md',
            '方案设计.md',
            '需求规格说明书.md',
            '设计报告.md',
        ]
        for fname in required_files:
            path = os.path.join(TEST_DIR, fname)
            self.assertTrue(os.path.exists(path), f"缺少必要文件: {fname}")

    def test_data_directory_structure(self):
        """测试数据目录结构"""
        self.assertTrue(os.path.isdir(DATA_DIR), "data目录不存在")
        required_data = ['processed_qa.json', 'qa_index.faiss', 'bm25.pkl', 'qa_meta.pkl']
        for fname in required_data:
            path = os.path.join(DATA_DIR, fname)
            self.assertTrue(os.path.exists(path), f"data目录缺少: {fname}")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("  智能制造知识库问答系统 - 自动化测试")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 按顺序加载测试类
    test_classes = [
        TestProjectStructure,
        TestDataPreprocessing,
        TestIndexFiles,
        TestDatabase,
        TestAPIInterface,
        TestRetrievalModule,
    ]
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("  ✅ 所有测试通过！")
    else:
        print(f"  ❌ 测试失败: {len(result.failures)} 失败, {len(result.errors)} 错误")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
