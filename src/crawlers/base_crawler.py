"""
基础爬虫类 - 所有爬虫的父类
"""
import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json

class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('USER_AGENT', 'MedLitAgent/1.0')
        })
        self.delay = config.get('CRAWL_DELAY', 1)
        self.max_papers = config.get('MAX_PAPERS_PER_QUERY', 1000)
        
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     headers: Optional[Dict] = None) -> requests.Response:
        """发送HTTP请求"""
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # 添加延迟以避免被封
            time.sleep(self.delay)
            
            return response
        except requests.RequestException as e:
            self.logger.error(f"请求失败: {url}, 错误: {e}")
            raise
    
    def _save_raw_data(self, data: Any, filename: str, data_type: str = 'json'):
        """保存原始数据"""
        import os
        from config.config import Config
        
        # 确保目录存在
        save_dir = os.path.join(Config.DATA_DIR, 'raw', self.__class__.__name__.lower())
        os.makedirs(save_dir, exist_ok=True)
        
        filepath = os.path.join(save_dir, filename)
        
        if data_type == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif data_type == 'text':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        self.logger.info(f"原始数据已保存: {filepath}")
    
    @abstractmethod
    def search_papers(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索论文 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """获取论文详细信息 - 子类必须实现"""
        pass
    
    def normalize_paper_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化论文数据格式"""
        return {
            'id': raw_data.get('id', ''),
            'title': raw_data.get('title', ''),
            'authors': raw_data.get('authors', []),
            'abstract': raw_data.get('abstract', ''),
            'keywords': raw_data.get('keywords', []),
            'publication_date': raw_data.get('publication_date', ''),
            'journal': raw_data.get('journal', ''),
            'doi': raw_data.get('doi', ''),
            'url': raw_data.get('url', ''),
            'source': self.__class__.__name__.replace('Crawler', '').lower(),
            'raw_data': raw_data
        }
    
    def crawl_by_keywords(self, keywords: List[str], max_results_per_keyword: int = 100) -> List[Dict[str, Any]]:
        """根据关键词批量爬取"""
        all_papers = []
        
        for keyword in keywords:
            self.logger.info(f"正在搜索关键词: {keyword}")
            try:
                papers = self.search_papers(keyword, max_results_per_keyword)
                all_papers.extend(papers)
                self.logger.info(f"关键词 '{keyword}' 找到 {len(papers)} 篇论文")
            except Exception as e:
                self.logger.error(f"搜索关键词 '{keyword}' 时出错: {e}")
                continue
        
        # 去重
        unique_papers = {}
        for paper in all_papers:
            paper_id = paper.get('id') or paper.get('doi') or paper.get('title')
            if paper_id and paper_id not in unique_papers:
                unique_papers[paper_id] = paper
        
        result = list(unique_papers.values())
        self.logger.info(f"总共找到 {len(result)} 篇唯一论文")
        return result