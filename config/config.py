"""
配置文件 - 医学文献爬取系统
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///medlit.db')
    
    # API配置
    PUBMED_API_KEY = os.getenv('PUBMED_API_KEY', '')
    PUBMED_EMAIL = os.getenv('PUBMED_EMAIL', 'your-email@example.com')
    
    # 爬虫配置
    CRAWL_DELAY = int(os.getenv('CRAWL_DELAY', '1'))  # 秒
    MAX_PAPERS_PER_QUERY = int(os.getenv('MAX_PAPERS_PER_QUERY', '1000'))
    USER_AGENT = 'MedLitAgent/1.0 (Medical Literature Crawler)'
    
    # NLP配置
    SPACY_MODEL = 'en_core_web_sm'
    MEDICAL_KEYWORDS_FILE = 'config/medical_keywords.json'
    
    # 文件路径
    DATA_DIR = 'data'
    PAPERS_DIR = os.path.join(DATA_DIR, 'papers')
    KEYWORDS_DIR = os.path.join(DATA_DIR, 'keywords')
    REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
    
    # Web服务配置
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 12000
    FLASK_DEBUG = True
    
    # 医学领域分类
    MEDICAL_CATEGORIES = {
        'cardiology': '心脏病学',
        'oncology': '肿瘤学',
        'neurology': '神经学',
        'immunology': '免疫学',
        'pharmacology': '药理学',
        'genetics': '遗传学',
        'infectious_diseases': '传染病学',
        'surgery': '外科学',
        'pediatrics': '儿科学',
        'psychiatry': '精神病学',
        'radiology': '放射学',
        'pathology': '病理学',
        'epidemiology': '流行病学',
        'public_health': '公共卫生',
        'clinical_trials': '临床试验'
    }
    
    # 数据源配置
    DATA_SOURCES = {
        'pubmed': {
            'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'enabled': True
        },
        'pmc': {
            'base_url': 'https://www.ncbi.nlm.nih.gov/pmc/',
            'enabled': True
        },
        'arxiv': {
            'base_url': 'http://export.arxiv.org/api/query',
            'enabled': True,
            'categories': ['q-bio', 'physics.med-ph']
        }
    }