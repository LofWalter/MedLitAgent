# MedLitAgent - 医学文献爬取和整理系统

MedLitAgent是一个智能的医学文献爬取和整理系统，能够从PubMed、arXiv等主要医学文献数据库中自动爬取文献，并使用先进的自然语言处理技术对文献进行关键词提取和分类整理。

## 🌟 主要功能

- **多数据源爬取**: 支持PubMed、arXiv等主要医学文献数据库
- **智能关键词提取**: 使用NLP技术自动提取医学关键词
- **自动分类**: 基于机器学习的医学领域自动分类
- **文献管理**: 完整的文献搜索、存储和管理功能
- **数据导出**: 支持CSV、Excel、JSON、PDF等多种格式导出
- **Web界面**: 用户友好的Web界面和RESTful API

## 🚀 快速开始

### 1. 环境要求

- **Python 3.12.9** (推荐版本)
- pip (最新版本)
- Git

### 2. 安装依赖

#### 方法一：使用 pip (推荐)
```bash
cd MedLitAgent

# 确保使用 Python 3.12.9
python --version  # 应该显示 Python 3.12.9

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 或者使用 pyproject.toml
pip install -e .
```

#### 方法二：使用 Docker
```bash
cd MedLitAgent

# 构建镜像
docker build -t medlitagent .

# 运行容器
docker run -p 12000:12000 medlitagent

# 或者使用 docker-compose
docker-compose up
```

#### 方法三：Python 版本管理
如果您需要安装 Python 3.12.9：

**使用 pyenv (Linux/macOS):**
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.12.9
pyenv install 3.12.9
pyenv local 3.12.9

# 验证版本
python --version
```

**使用 conda:**
```bash
# 创建新环境
conda create -n medlitagent python=3.12.9
conda activate medlitagent

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

复制环境配置文件并根据需要修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置PubMed API密钥等信息。

### 4. 运行系统

#### 命令行模式

```bash
# 爬取文献
python main.py crawl "machine learning" "deep learning" --sources pubmed arxiv --max-results 100

# 搜索文献
python main.py search --query "cancer" --category oncology --limit 10

# 导出文献
python main.py export --format excel --category cardiology --output cardiology_papers.xlsx

# 查看统计信息
python main.py stats
```

#### Web界面模式

```bash
python main.py web
```

然后在浏览器中访问 `http://localhost:12000`

## 📖 详细使用说明

### 命令行使用

#### 爬取文献

```bash
python main.py crawl [关键词...] [选项]
```

选项：
- `--sources`: 数据源选择 (pubmed, arxiv)
- `--max-results`: 每个关键词最大爬取数量
- `--output`: 输出文件路径

示例：
```bash
# 从PubMed和arXiv爬取机器学习相关论文
python main.py crawl "machine learning" "artificial intelligence" --sources pubmed arxiv --max-results 200

# 爬取心脏病学论文并导出为Excel
python main.py crawl "cardiology" "heart disease" --output cardiology.xlsx
```

#### 搜索文献

```bash
python main.py search [选项]
```

选项：
- `--query`: 搜索查询词
- `--category`: 分类过滤
- `--source`: 数据源过滤
- `--limit`: 结果数量限制

示例：
```bash
# 搜索包含"cancer"的论文
python main.py search --query "cancer" --limit 20

# 搜索肿瘤学分类的论文
python main.py search --category oncology --limit 50
```

#### 导出文献

```bash
python main.py export [选项]
```

选项：
- `--format`: 导出格式 (csv, excel, json, pdf, report)
- `--query`: 搜索查询词
- `--category`: 分类过滤
- `--source`: 数据源过滤
- `--limit`: 结果数量限制
- `--output`: 输出文件名

示例：
```bash
# 导出所有心脏病学论文为Excel格式
python main.py export --format excel --category cardiology --output cardiology_papers.xlsx

# 生成摘要报告
python main.py export --format report --output summary_report.html
```

### Web界面使用

启动Web服务后，可以通过浏览器访问以下功能：

1. **首页**: 系统概览和快速开始
2. **爬取文献**: 配置和启动爬取任务
3. **搜索文献**: 搜索和浏览已爬取的文献
4. **仪表板**: 查看统计信息和数据分析

### API使用

系统提供RESTful API接口：

```bash
# 健康检查
GET /api/health

# 获取统计信息
GET /api/statistics

# 开始爬取任务
POST /api/crawl
{
    "keywords": ["machine learning", "deep learning"],
    "sources": ["pubmed", "arxiv"],
    "max_results": 100
}

# 搜索论文
GET /api/papers?query=cancer&category=oncology&page=1&per_page=20

# 获取论文详情
GET /api/papers/{paper_id}

# 提取关键词
POST /api/extract-keywords
{
    "text": "论文文本内容..."
}

# 分类文本
POST /api/classify-text
{
    "text": "论文文本内容..."
}
```

## 🏗️ 系统架构

```
MedLitAgent/
├── config/                 # 配置文件
│   ├── config.py          # 主配置
│   └── medical_keywords.json # 医学关键词词典
├── src/                   # 源代码
│   ├── crawlers/          # 爬虫模块
│   │   ├── base_crawler.py
│   │   ├── pubmed_crawler.py
│   │   ├── arxiv_crawler.py
│   │   └── crawler_manager.py
│   ├── nlp/               # 自然语言处理
│   │   ├── keyword_extractor.py
│   │   └── text_classifier.py
│   ├── database/          # 数据库管理
│   │   ├── models.py
│   │   └── database_manager.py
│   ├── api/               # Web API
│   │   └── app.py
│   └── utils/             # 工具模块
│       └── export_utils.py
├── templates/             # Web模板
├── static/                # 静态文件
├── data/                  # 数据目录
├── tests/                 # 测试文件
└── main.py               # 主程序入口
```

## 🔧 配置说明

### 环境变量配置

在 `.env` 文件中配置以下变量：

```bash
# 数据库配置
DATABASE_URL=sqlite:///medlit.db

# PubMed API配置
PUBMED_API_KEY=your_api_key_here
PUBMED_EMAIL=your-email@example.com

# 爬虫配置
CRAWL_DELAY=1
MAX_PAPERS_PER_QUERY=1000

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### 医学分类配置

系统支持以下医学分类：

- 心脏病学 (cardiology)
- 肿瘤学 (oncology)
- 神经学 (neurology)
- 免疫学 (immunology)
- 药理学 (pharmacology)
- 遗传学 (genetics)
- 传染病学 (infectious_diseases)
- 外科学 (surgery)
- 儿科学 (pediatrics)
- 精神病学 (psychiatry)
- 放射学 (radiology)
- 病理学 (pathology)
- 流行病学 (epidemiology)
- 公共卫生 (public_health)
- 临床试验 (clinical_trials)

## 📊 数据格式

### 论文数据结构

```json
{
    "id": "论文ID",
    "external_id": "外部数据库ID",
    "title": "论文标题",
    "abstract": "摘要",
    "authors": ["作者1", "作者2"],
    "journal": "期刊名称",
    "publication_date": "2023-01-01",
    "doi": "DOI",
    "url": "论文URL",
    "source": "数据源",
    "predicted_category": "预测分类",
    "classification_confidence": 0.95,
    "extracted_keywords": [
        {
            "keyword": "关键词",
            "category": "分类",
            "score": 2.5,
            "methods": ["dictionary", "tfidf"]
        }
    ]
}
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/your-username/MedLitAgent/issues)
2. 创建新的 Issue
3. 联系开发团队

## 🙏 致谢

感谢以下开源项目：

- [PubMed API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [arXiv API](https://arxiv.org/help/api)
- [Flask](https://flask.palletsprojects.com/)
- [scikit-learn](https://scikit-learn.org/)
- [NLTK](https://www.nltk.org/)
- [spaCy](https://spacy.io/)
