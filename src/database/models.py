"""
数据库模型 - 定义医学文献数据的存储结构
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Paper(Base):
    """论文表"""
    __tablename__ = 'papers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=False)  # PubMed ID, arXiv ID等
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(JSON)  # 存储作者列表
    journal = Column(String(200))
    publication_date = Column(String(20))  # YYYY-MM-DD格式
    doi = Column(String(100))
    url = Column(String(500))
    source = Column(String(50), nullable=False)  # pubmed, arxiv等
    
    # 分类信息
    predicted_category = Column(String(50))
    classification_confidence = Column(Float)
    classification_probabilities = Column(JSON)
    
    # 关键词信息
    original_keywords = Column(JSON)  # 原始关键词
    extracted_keywords = Column(JSON)  # 提取的关键词
    keyword_categories = Column(JSON)  # 关键词分类
    
    # 元数据
    raw_data = Column(JSON)  # 原始爬取数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    keywords = relationship("Keyword", back_populates="paper")
    categories = relationship("PaperCategory", back_populates="paper")

class Keyword(Base):
    """关键词表"""
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    keyword = Column(String(200), nullable=False)
    category = Column(String(50))
    score = Column(Float)
    extraction_method = Column(String(50))  # dictionary, pattern, tfidf, ner
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", back_populates="keywords")

class Category(Base):
    """医学分类表"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))  # 中文显示名称
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    papers = relationship("PaperCategory", back_populates="category")

class PaperCategory(Base):
    """论文-分类关联表"""
    __tablename__ = 'paper_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    confidence = Column(Float)  # 分类置信度
    is_primary = Column(Boolean, default=False)  # 是否为主要分类
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", back_populates="categories")
    category = relationship("Category", back_populates="papers")

class CrawlSession(Base):
    """爬取会话表"""
    __tablename__ = 'crawl_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_name = Column(String(100))
    query = Column(Text)  # 搜索查询
    sources = Column(JSON)  # 数据源列表
    total_papers = Column(Integer, default=0)
    successful_papers = Column(Integer, default=0)
    failed_papers = Column(Integer, default=0)
    
    # 状态
    status = Column(String(20), default='running')  # running, completed, failed
    error_message = Column(Text)
    
    # 时间信息
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # 配置
    config = Column(JSON)

class SearchHistory(Base):
    """搜索历史表"""
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    filters = Column(JSON)  # 搜索过滤条件
    results_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Export(Base):
    """导出记录表"""
    __tablename__ = 'exports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    export_type = Column(String(20), nullable=False)  # csv, excel, pdf
    filename = Column(String(200))
    file_path = Column(String(500))
    query_filters = Column(JSON)  # 导出时的查询条件
    paper_count = Column(Integer)
    file_size = Column(Integer)  # 文件大小（字节）
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(50))
    message = Column(Text, nullable=False)
    details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)