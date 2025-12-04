#!/bin/bash

# MedLitAgent 安装脚本
# 确保使用 Python 3.12.9

set -e

echo "🚀 MedLitAgent 安装脚本"
echo "========================"

# 检查 Python 版本
echo "📋 检查 Python 版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+\.\d+')
REQUIRED_VERSION="3.12.9"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  警告: 当前 Python 版本是 $PYTHON_VERSION，推荐版本是 $REQUIRED_VERSION"
    echo "请考虑使用以下方法安装正确版本:"
    echo ""
    echo "使用 pyenv:"
    echo "  curl https://pyenv.run | bash"
    echo "  pyenv install 3.12.9"
    echo "  pyenv local 3.12.9"
    echo ""
    echo "使用 conda:"
    echo "  conda create -n medlitagent python=3.12.9"
    echo "  conda activate medlitagent"
    echo ""
    read -p "是否继续安装? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Python 版本正确: $PYTHON_VERSION"
fi

# 检查 pip
echo "📋 检查 pip..."
if ! command -v pip &> /dev/null; then
    echo "❌ pip 未找到，请先安装 pip"
    exit 1
fi

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 下载 NLTK 数据
echo "📚 下载 NLTK 数据..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print('✅ NLTK 数据下载完成')
except Exception as e:
    print(f'⚠️  NLTK 数据下载失败: {e}')
"

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data/{papers,keywords,reports,exports,models}
mkdir -p logs
mkdir -p static/{css,js,images}

# 检查配置文件
echo "⚙️  检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 配置文件，请根据需要修改"
    else
        echo "⚠️  未找到 .env.example 文件"
    fi
fi

# 运行测试
echo "🧪 运行系统测试..."
if python -c "
import sys
sys.path.append('.')
try:
    from config.config import Config
    from src.crawlers.crawler_manager import CrawlerManager
    from src.nlp.keyword_extractor import KeywordExtractor
    from src.database.database_manager import DatabaseManager
    print('✅ 所有模块导入成功')
except Exception as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
"; then
    echo "✅ 系统测试通过"
else
    echo "❌ 系统测试失败"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo "========================"
echo ""
echo "📖 使用说明:"
echo "  python main.py --help          # 查看帮助"
echo "  python demo.py                 # 运行演示"
echo "  python main.py stats           # 查看统计"
echo "  python main.py web             # 启动Web服务"
echo ""
echo "🌐 Web界面: http://localhost:12000"
echo "📚 文档: README.md, USAGE_GUIDE.md"
echo ""
echo "Happy researching! 🔬"