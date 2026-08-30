markdown
复制
下载
# 基于NLP的智能制造知识库问答系统

## 项目简介
构建一个面向智能制造领域的设备手册与故障知识智能问答平台。系统以工业技术文档、设备手册、故障案例库为基础，构建结构化的领域知识库，支持用户通过自然语言提问获取设备操作指导、故障诊断建议和技术参数查询。最终交付一个可交互的Web问答系统原型，实现知识的高效检索与智能问答。

## 数据集来源
- **PANDAX 工业 QAE 数据集**（官方托管地址）：  
  [https://doi.org/10.5281/zenodo.14510798](https://doi.org/10.5281/zenodo.14510798)  
- 备选下载渠道（海数据平台）：  
  [https://haidatas.com/dataset/pandax_based_gongyexitongwendajieshishujuj_72e1985a](https://haidatas.com/dataset/pandax_based_gongyexitongwendajieshishujuj_72e1985a)

该数据集聚焦工业系统信息问答和技术文档理解，包含 **1860个QAE三元组**，涵盖冷却系统、绿色技术等工业领域。

## 数据预处理
1. 原始数据压缩包 `14510798.zip` 解压后得到 `PANDAX_dataset.json` 和 `PDF_patens.zip`。
2. 运行预处理脚本 `preprocess.py`，读取 JSON 文件，提取问答对，进行文本清洗，生成 `data/processed_qa.json`。
3. 该预处理结果将用于后续知识库索引构建（Elasticsearch + Faiss）。

## 项目结构
├── data/
│ ├── 14510798.zip # 原始数据集压缩包
│ ├── raw_data/ # 解压后的原始数据
│ │ ├── PANDAX_dataset.json
│ │ └── PDF_patens.zip
│ └── processed_qa.json # 预处理后的问答对（由 preprocess.py 生成）
├── prompt/
│ ├── 20260826_daily_log.json
│ └── 20260830_daily_log.json # 今日AI对话日志
├── preprocess.py # 数据预处理脚本
├── 方案设计.md
├── 选题说明.md
├── 学习笔记.md
└── README.md

text
复制
下载

## 后续工作
- 构建知识库索引（Elasticsearch 全文检索 + Faiss 向量检索）
- 实现问题理解、多路召回、答案排序模块
- 开发前后端交互界面