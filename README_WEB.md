# MedLitAgent Web界面使用指南

## 🌟 功能概述

MedLitAgent是一个强大的医学文献爬取和整理系统，提供了直观的Web界面来管理和分析医学文献。

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install python-dotenv flask flask-cors beautifulsoup4 requests pandas scikit-learn nltk sqlalchemy
```

### 2. 启动Web服务

```bash
python main.py web --host 0.0.0.0 --port 12000
```

### 3. 访问Web界面

- **主页**: http://localhost:12000
- **仪表板**: http://localhost:12000/dashboard  
- **搜索页面**: http://localhost:12000/search
- **爬取页面**: http://localhost:12000/crawl

## 📊 主要功能

### 1. 仪表板 (Dashboard)
- 📈 实时统计信息展示
- 📊 分类和数据源分布图表
- 📝 最新论文列表
- 🔥 热门关键词展示

### 2. 搜索功能 (Search)
- 🔍 高级搜索表单
- 🏷️ 多维度过滤（分类、数据源、日期）
- 📄 分页结果展示
- 📤 多格式导出（CSV、Excel、JSON、PDF）

### 3. 爬取功能 (Crawl)
- 🕷️ 多数据源支持（PubMed、arXiv）
- 🎯 关键词批量爬取
- ⚙️ 可配置爬取参数
- 📊 实时进度显示

## 🔧 API端点

### 健康检查
```
GET /api/health
```

### 统计信息
```
GET /api/statistics
```

### 搜索论文
```
POST /api/search
Content-Type: application/json
{
  "query": "machine learning",
  "category": "AI",
  "source": "arxiv",
  "limit": 20,
  "offset": 0
}
```

### 获取分类
```
GET /api/categories
```

### 热门关键词
```
GET /api/keywords/popular?limit=10
```

### 导出数据
```
GET /api/export?format=csv&query=covid&limit=100
POST /api/export
Content-Type: application/json
{
  "format": "excel",
  "query": "covid-19",
  "category": "Medicine",
  "limit": 500
}
```

### 爬取文献
```
POST /api/crawl
Content-Type: application/json
{
  "keywords": ["machine learning", "deep learning"],
  "sources": ["pubmed", "arxiv"],
  "max_results": 100
}
```

## 🎨 界面特性

### 响应式设计
- 📱 移动端友好
- 💻 桌面端优化
- 🎯 直观的用户体验

### 实时数据
- ⚡ AJAX异步加载
- 🔄 自动刷新统计
- 📊 动态图表更新

### 交互功能
- 🔍 实时搜索建议
- 📋 一键复制功能
- 💾 批量操作支持

## 🛠️ 配置选项

### 环境变量 (.env)
```env
# 数据库配置
DATABASE_URL=sqlite:///medlit.db

# Flask配置
FLASK_HOST=0.0.0.0
FLASK_PORT=12000
FLASK_DEBUG=True

# 爬虫配置
CRAWL_DELAY=1
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# 导出配置
EXPORT_DIR=exports
MAX_EXPORT_SIZE=10000
```

## 🧪 测试

运行Web服务测试：

```bash
python test_web.py
```

测试包括：
- ✅ 健康检查
- 📊 统计信息获取
- 🏷️ 分类信息获取
- 🌐 页面访问测试
- 🔗 API端点验证

## 📁 目录结构

```
MedLitAgent/
├── src/
│   ├── api/           # Web API
│   ├── crawlers/      # 爬虫模块
│   ├── database/      # 数据库管理
│   └── nlp/          # 自然语言处理
├── templates/         # HTML模板
├── static/           # 静态资源
├── data/             # 数据存储
├── exports/          # 导出文件
└── logs/             # 日志文件
```

## 🔍 使用示例

### 1. 爬取COVID-19相关文献
```bash
python main.py crawl "covid-19" "coronavirus" --sources pubmed arxiv --max-results 200
```

### 2. 搜索机器学习论文
```bash
python main.py search --query "machine learning" --category "AI" --limit 50
```

### 3. 导出数据
```bash
python main.py export --format excel --query "deep learning" --limit 1000 --output ml_papers.xlsx
```

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用
   - 确认所有依赖已安装
   - 查看错误日志

2. **数据库连接错误**
   - 检查DATABASE_URL配置
   - 确认数据库文件权限
   - 重新初始化数据库

3. **爬取失败**
   - 检查网络连接
   - 验证API密钥配置
   - 调整爬取延迟设置

### 日志查看
```bash
tail -f logs/medlit.log
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见LICENSE文件