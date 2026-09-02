@echo off
chcp 65001 >nul
title 智能制造知识库问答系统
echo ========================================
echo   智能制造知识库问答系统 - 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import flask, jieba, faiss, sentence_transformers, rank_bm25" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包，请稍候...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

REM 检查预处理数据是否存在
if not exist "data\processed_qa.json" (
    echo [提示] 正在进行数据预处理...
    python preprocess.py
    if errorlevel 1 (
        echo [错误] 数据预处理失败
        pause
        exit /b 1
    )
)

REM 检查索引是否存在
if not exist "data\qa_index.faiss" (
    echo [提示] 正在构建知识库索引（首次运行约需1-3分钟）...
    python build_index.py
    if errorlevel 1 (
        echo [错误] 索引构建失败
        pause
        exit /b 1
    )
)

echo.
echo [完成] 环境检查通过，正在启动后端服务...
echo [信息] 后端API地址: http://127.0.0.1:5000
echo [信息] 前端页面将自动在浏览器中打开
echo [信息] 首次启动加载模型约需10-30秒，请耐心等待
echo.
echo 停止服务请按 Ctrl+C，或直接关闭此窗口
echo.

REM 延迟5秒后自动打开前端页面
start "" /min cmd /c "timeout /t 8 /nobreak >nul && start "" "" "%~dp0index.html""

REM 启动后端服务
python app.py

pause
