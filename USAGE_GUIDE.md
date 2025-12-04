# MedLitAgent 使用指南

## 🚀 快速开始

### 1. 系统要求
- **Python 3.12.9** (推荐版本，确保最佳兼容性)
- 至少 2GB 内存
- 网络连接（用于爬取文献）
- Git (用于克隆项目)

### 2. 安装和配置

#### 快速安装（推荐）
```bash
# 克隆项目
git clone https://github.com/LofWalter/MedLitAgent.git
cd MedLitAgent

# 运行安装脚本
# Linux/macOS:
chmod +x install.sh
./install.sh

# Windows:
install.bat
```

#### 手动安装
```bash
# 确保使用 Python 3.12.9
python --version  # 应该显示 Python 3.12.9

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 下载NLTK数据
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# 运行演示
python demo.py
```

#### Docker 安装
```bash
# 使用 Docker
docker build -t medlitagent .
docker run -p 12000:12000 medlitagent

# 或使用 docker-compose
docker-compose up
```

### 3. 基本使用

#### 查看帮助
```bash
python main.py --help
```

#### 查看系统统计
```bash
python main.py stats
```

## 📚 功能详解

### 1. 文献爬取

#### 基本爬取
```bash
# 爬取机器学习相关论文
python main.py crawl "machine learning" --sources pubmed --max-results 50

# 爬取多个关键词
python main.py crawl "cancer" "oncology" "tumor" --sources pubmed arxiv --max-results 100

# 爬取并直接导出
python main.py crawl "cardiology" --sources pubmed --max-results 200 --output cardiology_papers.csv
```

#### 支持的数据源
- **PubMed**: 最大的生物医学文献数据库
- **arXiv**: 预印本论文数据库（包含医学相关论文）

#### 爬取参数说明
- `keywords`: 搜索关键词（必需）
- `--sources`: 数据源选择，默认为 pubmed arxiv
- `--max-results`: 每个关键词最大爬取数量，默认100
- `--output`: 输出文件路径（可选）

### 2. 文献搜索

#### 基本搜索
```bash
# 搜索包含特定词汇的论文
python main.py search --query "deep learning"

# 按分类搜索
python main.py search --category oncology --limit 20

# 按数据源搜索
python main.py search --source pubmed --limit 30

# 组合搜索
python main.py search --query "AI" --category neurology --limit 10
```

#### 搜索参数说明
- `--query`: 搜索查询词
- `--category`: 医学分类过滤
- `--source`: 数据源过滤
- `--limit`: 结果数量限制，默认20

### 3. 数据导出

#### 支持的导出格式
```bash
# CSV格式
python main.py export --format csv --category cardiology --output heart_papers.csv

# Excel格式
python main.py export --format excel --query "cancer" --output cancer_research.xlsx

# JSON格式
python main.py export --format json --source pubmed --output pubmed_papers.json

# PDF报告
python main.py export --format pdf --category oncology --output oncology_report.pdf

# HTML摘要报告
python main.py export --format report --output summary_report.html
```

#### 导出参数说明
- `--format`: 导出格式（csv, excel, json, pdf, report）
- `--query`: 搜索过滤
- `--category`: 分类过滤
- `--source`: 数据源过滤
- `--limit`: 导出数量限制
- `--output`: 输出文件名

### 4. Web界面

#### 启动Web服务
```bash
python main.py web
```

访问 `http://localhost:12000` 使用Web界面。

#### Web功能
- **首页**: 系统概览和统计信息
- **爬取文献**: 配置和启动爬取任务
- **搜索文献**: 搜索和浏览已爬取的文献
- **仪表板**: 数据分析和可视化

## 🔧 高级配置

### 1. 环境变量配置

创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=sqlite:///medlit.db

# PubMed API配置（可选，提高爬取速度）
PUBMED_API_KEY=your_api_key_here
PUBMED_EMAIL=your-email@example.com

# 爬虫配置
CRAWL_DELAY=1
MAX_PAPERS_PER_QUERY=1000

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=12000
```

### 2. 医学分类系统

系统支持15个主要医学分类：

1. **cardiology** - 心脏病学
2. **oncology** - 肿瘤学
3. **neurology** - 神经学
4. **immunology** - 免疫学
5. **pharmacology** - 药理学
6. **genetics** - 遗传学
7. **infectious_diseases** - 传染病学
8. **surgery** - 外科学
9. **pediatrics** - 儿科学
10. **psychiatry** - 精神病学
11. **radiology** - 放射学
12. **pathology** - 病理学
13. **epidemiology** - 流行病学
14. **public_health** - 公共卫生
15. **clinical_trials** - 临床试验

### 3. 关键词提取配置

系统使用多种方法提取关键词：
- **医学词典匹配**: 基于预定义的医学术语词典
- **TF-IDF**: 基于词频-逆文档频率的统计方法
- **词性标注**: 提取名词和形容词作为候选关键词
- **spaCy NER**: 命名实体识别（如果安装了spaCy）

## 📊 API接口

### RESTful API端点

#### 健康检查
```bash
GET /api/health
```

#### 获取统计信息
```bash
GET /api/statistics
```

#### 开始爬取任务
```bash
POST /api/crawl
Content-Type: application/json

{
    "keywords": ["machine learning", "deep learning"],
    "sources": ["pubmed", "arxiv"],
    "max_results": 100
}
```

#### 搜索论文
```bash
GET /api/papers?query=cancer&category=oncology&page=1&per_page=20
```

#### 获取论文详情
```bash
GET /api/papers/{paper_id}
```

#### 提取关键词
```bash
POST /api/extract-keywords
Content-Type: application/json

{
    "text": "论文文本内容..."
}
```

#### 分类文本
```bash
POST /api/classify-text
Content-Type: application/json

{
    "text": "论文文本内容..."
}
```

## 🛠️ 故障排除

### 常见问题

#### 1. NLTK数据缺失
```bash
# 下载所需的NLTK数据
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"
```

#### 2. 爬取速度慢
- 配置PubMed API密钥
- 减少并发请求数量
- 增加爬取延迟

#### 3. 内存不足
- 减少批处理大小
- 分批处理大量数据
- 增加系统内存

#### 4. 分类准确度低
- 增加训练数据
- 调整分类器参数
- 使用更好的特征提取方法

### 日志查看
```bash
# 查看日志文件
tail -f logs/medlit_$(date +%Y%m%d).log
```

## 📈 性能优化

### 1. 数据库优化
- 使用PostgreSQL替代SQLite（大数据量）
- 创建适当的索引
- 定期清理过期数据

### 2. 爬虫优化
- 使用代理池
- 实现断点续传
- 添加缓存机制

### 3. NLP优化
- 安装spaCy和医学模型
- 使用GPU加速
- 预训练领域特定模型

## 🔒 安全注意事项

1. **API密钥管理**: 不要在代码中硬编码API密钥
2. **访问控制**: 在生产环境中添加身份验证
3. **数据隐私**: 遵守相关的数据保护法规
4. **爬虫礼仪**: 遵守网站的robots.txt和使用条款

## 📞 技术支持

如果遇到问题：

1. 查看日志文件
2. 检查网络连接
3. 验证配置文件
4. 查看GitHub Issues
5. 联系开发团队

## 🎯 最佳实践

1. **定期备份数据库**
2. **监控系统资源使用**
3. **定期更新医学词典**
4. **验证爬取数据质量**
5. **优化关键词选择**

---

更多详细信息请参考项目文档和源代码注释。