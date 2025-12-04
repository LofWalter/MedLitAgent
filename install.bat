@echo off
REM MedLitAgent Windows 安装脚本
REM 确保使用 Python 3.12.9

echo 🚀 MedLitAgent Windows 安装脚本
echo ================================

REM 检查 Python 版本
echo 📋 检查 Python 版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未找到，请先安装 Python 3.12.9
    echo 下载地址: https://www.python.org/downloads/release/python-3129/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 当前 Python 版本: %PYTHON_VERSION%

REM 检查版本是否为 3.12.9
echo %PYTHON_VERSION% | findstr "3.12.9" >nul
if errorlevel 1 (
    echo ⚠️  警告: 推荐使用 Python 3.12.9
    echo 当前版本: %PYTHON_VERSION%
    set /p CONTINUE="是否继续安装? (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
) else (
    echo ✅ Python 版本正确: %PYTHON_VERSION%
)

REM 检查 pip
echo 📋 检查 pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip 未找到，请先安装 pip
    pause
    exit /b 1
)

REM 升级 pip
echo ⬆️  升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 下载 NLTK 数据
echo 📚 下载 NLTK 数据...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); print('✅ NLTK 数据下载完成')"

REM 创建必要的目录
echo 📁 创建目录结构...
if not exist "data" mkdir data
if not exist "data\papers" mkdir data\papers
if not exist "data\keywords" mkdir data\keywords
if not exist "data\reports" mkdir data\reports
if not exist "data\exports" mkdir data\exports
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images

REM 检查配置文件
echo ⚙️  检查配置文件...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ 已创建 .env 配置文件，请根据需要修改
    ) else (
        echo ⚠️  未找到 .env.example 文件
    )
)

REM 运行测试
echo 🧪 运行系统测试...
python -c "import sys; sys.path.append('.'); from config.config import Config; from src.crawlers.crawler_manager import CrawlerManager; from src.nlp.keyword_extractor import KeywordExtractor; from src.database.database_manager import DatabaseManager; print('✅ 所有模块导入成功')"
if errorlevel 1 (
    echo ❌ 系统测试失败
    pause
    exit /b 1
)

echo.
echo 🎉 安装完成！
echo ================================
echo.
echo 📖 使用说明:
echo   python main.py --help          # 查看帮助
echo   python demo.py                 # 运行演示
echo   python main.py stats           # 查看统计
echo   python main.py web             # 启动Web服务
echo.
echo 🌐 Web界面: http://localhost:12000
echo 📚 文档: README.md, USAGE_GUIDE.md
echo.
echo Happy researching! 🔬
pause