# 基于NLP的智能制造知识库问答系统

## 项目简介

构建一个面向智能制造领域的设备手册与故障知识智能问答平台。系统以工业技术文档、设备手册、故障案例库为基础，构建结构化的领域知识库，支持用户通过自然语言提问获取设备操作指导、故障诊断建议和技术参数查询。最终交付一个可交互的Web问答系统原型，实现知识的高效检索与智能问答。

本项目为《制造智能技术》课程设计成果，采用B/S架构，涵盖前端UI、后端服务、数据库、算法模块四个完整层级。

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 前端 | Vue3 + Element Plus + Axios（CDN引入，无需Node.js） |
| 后端 | Python Flask + RESTful API |
| 数据库 | SQLite 3（问答日志存储） |
| 检索引擎 | BM25（全文检索）+ Faiss（向量检索）多路召回 |
| NLP | Sentence-BERT（文本向量化）+ Jieba（中文分词） |
| 版本控制 | Git |

## 技术方向覆盖（课程要求至少3个）

1. **Web前端开发**：Vue3框架构建问答交互界面，对话式UI、知识卡片展示、结果高亮
2. **后端开发与算法**：Python Flask搭建后端服务，RESTful API接口，集成NLP处理模块
3. **自然语言处理**：文本预处理、语义理解、相似度计算，问题意图识别与答案检索
4. **数据分析与可视化**：问答日志统计分析，高频问题、检索耗时等指标

## 数据集来源

- **PANDAX 工业 QAE 数据集**（官方托管地址）：
  [https://doi.org/10.5281/zenodo.14510798](https://doi.org/10.5281/zenodo.14510798)
- 该数据集聚焦工业系统信息问答和技术文档理解，包含 **1860个QAE三元组**，涵盖冷却系统、绿色技术等工业领域。

## 快速开始

### 方式一：一键启动（推荐）

双击运行 `run.bat`，脚本会自动检查依赖、预处理数据、构建索引并启动服务。

### 方式二：手动启动

**1. 安装依赖**
```bash
pip install -r requirements.txt
```

**2. 数据预处理**（如data/processed_qa.json已存在可跳过）
```bash
python preprocess.py
```

**3. 构建知识库索引**（如data/qa_index.faiss已存在可跳过）
```bash
python build_index.py
```

**4. 初始化数据库**
```bash
python database.py
```

**5. 启动后端服务**
```bash
python app.py
```

**6. 打开前端页面**

用浏览器直接打开 `index.html` 文件，或访问 `http://127.0.0.1:5000` 确认后端运行。

### 运行自动化测试
```bash
python test_system.py
```

## 项目结构

```
├── data/
│   ├── 14510798.zip          # 原始数据集压缩包
│   ├── raw_data/              # 解压后的原始数据
│   │   └── PANDAX_dataset.json
│   ├── processed_qa.json      # 预处理后的问答对
│   ├── qa_index.faiss         # Faiss向量索引
│   ├── bm25.pkl               # BM25全文索引
│   ├── qa_meta.pkl            # 问答对元数据
│   └── qa_system.db           # SQLite数据库（运行时生成）
├── prompt/
│   ├── 20260826_daily_log.json
│   ├── 20260830_daily_log.json
│   └── 20260902_daily_log.json
├── app.py                      # Flask后端服务（含问答/统计/历史/健康检查API）
├── preprocess.py               # 数据预处理脚本
├── build_index.py              # 知识库索引构建脚本
├── database.py                 # SQLite数据库模块
├── test_system.py              # 自动化测试脚本
├── index.html                  # 前端页面（Vue3 + Element Plus）
├── run.bat                     # 一键启动脚本
├── requirements.txt            # Python依赖清单
├── README.md                   # 项目说明文档
├── 选题说明.md                 # 选题说明（含技术方向映射表、架构草图）
├── 方案设计.md                 # 方案设计文档
├── 需求规格说明书.md            # 需求规格说明书
├── 设计报告.md                 # 完整设计报告
└── 学习笔记.md                 # Vibe Coding学习笔记
```

## API接口文档

### 1. 问答接口

**请求：** `POST /ask`
**Content-Type：** `application/json`

```json
{
  "question": "冷却系统有哪些类型？"
}
```

**响应：**
```json
{
  "question": "冷却系统有哪些类型？",
  "results": [
    {
      "question": "冷却系统的分类有哪些？",
      "answer": "冷却系统按冷却介质可分为...",
      "score": 4.5
    }
  ],
  "latency_ms": 320
}
```

### 2. 统计接口

**请求：** `GET /stats`

**响应：**
```json
{
  "total_knowledge": 1860,
  "total_logs": 42,
  "avg_latency_ms": 285.5,
  "hot_questions": [
    {"question": "冷却系统有哪些类型？", "cnt": 5}
  ]
}
```

### 3. 历史记录接口

**请求：** `GET /history?limit=20`

**响应：**
```json
{
  "logs": [
    {
      "id": 1,
      "question": "冷却系统有哪些类型？",
      "top_question": "冷却系统的分类有哪些？",
      "top_answer": "...",
      "score": 4.5,
      "latency_ms": 320,
      "created_at": "2026-09-02 15:30:00"
    }
  ],
  "count": 20
}
```

### 4. 健康检查接口

**请求：** `GET /health`

**响应：**
```json
{
  "status": "ok",
  "knowledge_count": 1860
}
```

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue3 + Element Plus)        │
│  问答页 │ 知识库页 │ 历史记录页 │ 统计看板页         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / RESTful API
┌──────────────────────▼──────────────────────────────┐
│                    后端 (Python Flask)                │
│  问题理解 │ 多路召回(BM25+Faiss) │ 融合排序 │ 日志  │
└──────┬───────────────┬────────────────┬─────────────┘
       │               │                │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  BM25全文   │ │ Faiss向量   │ │ SQLite      │
│  倒排索引   │ │  检索索引   │ │  问答日志   │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 算法说明

### 多路召回策略

系统采用BM25全文检索与Faiss向量检索相结合的多路召回策略：

1. **BM25检索**：基于词频和逆文档频率的概率检索模型，擅长关键词精确匹配。使用Jieba对问题进行中文分词后计算BM25得分。
2. **向量检索**：使用Sentence-BERT（paraphrase-multilingual-MiniLM-L12-v2）将问题编码为384维向量，使用Faiss的IndexFlatIP进行内积相似度搜索，擅长语义相似度匹配。
3. **融合排序**：采用RRF（Reciprocal Rank Fusion）思想，对两路检索结果按排名加权融合，取Top-5返回。

## 提交物清单

- [x] 代码仓库（Git，含完整提交历史）
- [x] 运行脚本（run.bat）
- [x] README文档
- [x] 需求规格说明书
- [x] 设计报告
- [x] 过程档案（prompt日志）
- [x] 自动化测试
- [ ] 3分钟演示视频（需自行录制）

## 许可证

本项目为课程设计作业，仅供学习交流使用。
