@echo off
chcp 65001 >nul
echo ========================================
echo   智能制造知识库问答系统 - 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import flask, jieba, faiss, sentence_transformers, rank_bm25" >nul 2>&1
if errorlevel 1 (
    echo ⚙️  正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查预处理数据是否存在
if not exist "data\processed_qa.json" (
    echo ⚙️  正在进行数据预处理...
    python preprocess.py
    if errorlevel 1 (
        echo ❌ 数据预处理失败
        pause
        exit /b 1
    )
)

REM 检查索引是否存在
if not exist "data\qa_index.faiss" (
    echo ⚙️  正在构建知识库索引...
    python build_index.py
    if errorlevel 1 (
        echo ❌ 索引构建失败
        pause
        exit /b 1
    )
)

echo.
echo ✅ 环境检查完成，启动后端服务...
echo 📡 后端API: http://127.0.0.1:5000
echo 📄 前端页面: 用浏览器打开 index.html
echo.
echo 按 Ctrl+C 停止服务
echo.

python app.py
pause
