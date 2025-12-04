#!/usr/bin/env python3
"""
版本检查脚本
检查 Python 版本和依赖包版本是否符合要求
"""

import sys
import subprocess
import pkg_resources
from packaging import version

# 要求的 Python 版本
REQUIRED_PYTHON_VERSION = "3.12.9"

# 关键依赖包的最低版本要求
REQUIRED_PACKAGES = {
    'requests': '2.32.0',
    'beautifulsoup4': '4.12.0',
    'pandas': '2.2.0',
    'numpy': '1.26.0',
    'scikit-learn': '1.4.0',
    'nltk': '3.8.1',
    'sqlalchemy': '2.0.25',
    'flask': '3.0.0',
    'flask-cors': '4.0.0',
    'python-dotenv': '1.0.0',
}

def check_python_version():
    """检查 Python 版本"""
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    print(f"🐍 Python 版本检查")
    print(f"   当前版本: {current_version}")
    print(f"   推荐版本: {REQUIRED_PYTHON_VERSION}")
    
    if current_version == REQUIRED_PYTHON_VERSION:
        print("   ✅ Python 版本完全匹配")
        return True
    elif version.parse(current_version) >= version.parse("3.12.0"):
        print("   ⚠️  Python 版本兼容但不是推荐版本")
        return True
    else:
        print("   ❌ Python 版本过低，可能存在兼容性问题")
        return False

def check_package_versions():
    """检查依赖包版本"""
    print(f"\n📦 依赖包版本检查")
    
    all_good = True
    installed_packages = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}
    
    for package, required_version in REQUIRED_PACKAGES.items():
        package_lower = package.lower()
        
        if package_lower in installed_packages:
            current_version = installed_packages[package_lower]
            
            if version.parse(current_version) >= version.parse(required_version):
                print(f"   ✅ {package}: {current_version} (>= {required_version})")
            else:
                print(f"   ❌ {package}: {current_version} (需要 >= {required_version})")
                all_good = False
        else:
            print(f"   ❌ {package}: 未安装")
            all_good = False
    
    return all_good

def check_optional_packages():
    """检查可选依赖包"""
    print(f"\n🔧 可选依赖包检查")
    
    optional_packages = {
        'spacy': '用于增强的命名实体识别',
        'openpyxl': '用于 Excel 文件导出',
        'reportlab': '用于 PDF 报告生成',
        'torch': '用于深度学习模型（可选）',
    }
    
    installed_packages = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}
    
    for package, description in optional_packages.items():
        package_lower = package.lower()
        
        if package_lower in installed_packages:
            current_version = installed_packages[package_lower]
            print(f"   ✅ {package}: {current_version} - {description}")
        else:
            print(f"   ⚪ {package}: 未安装 - {description}")

def check_system_info():
    """检查系统信息"""
    print(f"\n💻 系统信息")
    print(f"   操作系统: {sys.platform}")
    print(f"   Python 路径: {sys.executable}")
    print(f"   Python 实现: {sys.implementation.name}")
    
    # 检查内存（如果可能）
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   总内存: {memory.total / (1024**3):.1f} GB")
        print(f"   可用内存: {memory.available / (1024**3):.1f} GB")
    except ImportError:
        print(f"   内存信息: 无法获取 (需要安装 psutil)")

def run_basic_tests():
    """运行基本功能测试"""
    print(f"\n🧪 基本功能测试")
    
    tests = [
        ("导入 config 模块", "from config.config import Config"),
        ("导入 crawler 模块", "from src.crawlers.crawler_manager import CrawlerManager"),
        ("导入 NLP 模块", "from src.nlp.keyword_extractor import KeywordExtractor"),
        ("导入 database 模块", "from src.database.database_manager import DatabaseManager"),
        ("NLTK 数据检查", "import nltk; nltk.data.find('tokenizers/punkt')"),
    ]
    
    all_passed = True
    
    for test_name, test_code in tests:
        try:
            exec(test_code)
            print(f"   ✅ {test_name}")
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 MedLitAgent 环境检查")
    print("=" * 60)
    
    # 检查 Python 版本
    python_ok = check_python_version()
    
    # 检查依赖包版本
    packages_ok = check_package_versions()
    
    # 检查可选包
    check_optional_packages()
    
    # 检查系统信息
    check_system_info()
    
    # 运行基本测试
    tests_ok = run_basic_tests()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 检查总结")
    print("=" * 60)
    
    if python_ok and packages_ok and tests_ok:
        print("🎉 所有检查通过！系统已准备就绪。")
        print("\n📖 下一步:")
        print("   python demo.py                 # 运行演示")
        print("   python main.py web             # 启动Web服务")
        print("   python main.py --help          # 查看帮助")
        return 0
    else:
        print("⚠️  发现问题，请解决后重新运行检查。")
        print("\n🔧 解决方案:")
        
        if not python_ok:
            print("   - 安装 Python 3.12.9")
            print("   - 使用 pyenv: pyenv install 3.12.9 && pyenv local 3.12.9")
            print("   - 使用 conda: conda create -n medlitagent python=3.12.9")
        
        if not packages_ok:
            print("   - 升级依赖包: pip install --upgrade -r requirements.txt")
            print("   - 重新安装: pip install -r requirements.txt --force-reinstall")
        
        if not tests_ok:
            print("   - 下载 NLTK 数据: python -c \"import nltk; nltk.download('punkt_tab')\"")
            print("   - 检查项目结构是否完整")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())