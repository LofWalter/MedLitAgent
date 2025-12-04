"""
爬虫管理器 - 统一管理所有爬虫
"""
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from datetime import datetime

from .pubmed_crawler import PubMedCrawler
from .arxiv_crawler import ArxivCrawler
from config.config import Config

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = Config.__dict__
        
        self.config = config
        self.crawlers = {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化爬虫
        self._init_crawlers()
        
        # 确保数据目录存在
        os.makedirs(config.get('DATA_DIR', 'data'), exist_ok=True)
        os.makedirs(config.get('PAPERS_DIR', 'data/papers'), exist_ok=True)
    
    def _init_crawlers(self):
        """初始化所有爬虫"""
        data_sources = self.config.get('DATA_SOURCES', {})
        
        if data_sources.get('pubmed', {}).get('enabled', False):
            self.crawlers['pubmed'] = PubMedCrawler(self.config)
            self.logger.info("PubMed爬虫已初始化")
        
        if data_sources.get('arxiv', {}).get('enabled', False):
            self.crawlers['arxiv'] = ArxivCrawler(self.config)
            self.logger.info("arXiv爬虫已初始化")
    
    def crawl_by_keywords(self, keywords: List[str], sources: Optional[List[str]] = None,
                         max_results_per_keyword: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """根据关键词从多个数据源爬取"""
        if sources is None:
            sources = list(self.crawlers.keys())
        
        results = {}
        
        for source in sources:
            if source not in self.crawlers:
                self.logger.warning(f"未找到数据源: {source}")
                continue
            
            self.logger.info(f"开始从 {source} 爬取数据")
            crawler = self.crawlers[source]
            
            try:
                papers = crawler.crawl_by_keywords(keywords, max_results_per_keyword)
                results[source] = papers
                self.logger.info(f"从 {source} 爬取到 {len(papers)} 篇论文")
            except Exception as e:
                self.logger.error(f"从 {source} 爬取时出错: {e}")
                results[source] = []
        
        return results
    
    def crawl_by_medical_categories(self, categories: List[str], sources: Optional[List[str]] = None,
                                  max_results_per_category: int = 100) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """根据医学分类爬取"""
        if sources is None:
            sources = list(self.crawlers.keys())
        
        results = {}
        
        for source in sources:
            if source not in self.crawlers:
                continue
            
            results[source] = {}
            crawler = self.crawlers[source]
            
            for category in categories:
                self.logger.info(f"从 {source} 爬取分类: {category}")
                
                try:
                    if hasattr(crawler, 'search_by_medical_category'):
                        papers = crawler.search_by_medical_category(category, max_results_per_category)
                    else:
                        # 使用通用搜索
                        papers = crawler.search_papers(category, max_results_per_category)
                    
                    results[source][category] = papers
                    self.logger.info(f"分类 {category} 从 {source} 爬取到 {len(papers)} 篇论文")
                    
                except Exception as e:
                    self.logger.error(f"爬取分类 {category} 从 {source} 时出错: {e}")
                    results[source][category] = []
        
        return results
    
    def parallel_crawl(self, queries: List[str], sources: Optional[List[str]] = None,
                      max_workers: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """并行爬取多个查询"""
        if sources is None:
            sources = list(self.crawlers.keys())
        
        results = {source: [] for source in sources}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_source_query = {}
            
            for source in sources:
                if source not in self.crawlers:
                    continue
                
                crawler = self.crawlers[source]
                for query in queries:
                    future = executor.submit(crawler.search_papers, query, 50)
                    future_to_source_query[future] = (source, query)
            
            # 收集结果
            for future in as_completed(future_to_source_query):
                source, query = future_to_source_query[future]
                try:
                    papers = future.result()
                    results[source].extend(papers)
                    self.logger.info(f"查询 '{query}' 从 {source} 完成，获得 {len(papers)} 篇论文")
                except Exception as e:
                    self.logger.error(f"查询 '{query}' 从 {source} 失败: {e}")
        
        return results
    
    def save_crawl_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存爬取结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawl_results_{timestamp}.json"
        
        filepath = os.path.join(self.config.get('PAPERS_DIR', 'data/papers'), filename)
        
        # 添加元数据
        output_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_papers': sum(len(papers) if isinstance(papers, list) else 
                                  sum(len(p) for p in papers.values()) if isinstance(papers, dict) else 0 
                                  for papers in results.values()),
                'sources': list(results.keys())
            },
            'data': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"爬取结果已保存到: {filepath}")
        return filepath
    
    def load_crawl_results(self, filepath: str) -> Dict[str, Any]:
        """加载爬取结果"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.logger.error(f"加载爬取结果失败: {e}")
            return {}
    
    def get_crawler_stats(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        stats = {
            'available_crawlers': list(self.crawlers.keys()),
            'total_crawlers': len(self.crawlers),
            'config': {
                'max_papers_per_query': self.config.get('MAX_PAPERS_PER_QUERY', 1000),
                'crawl_delay': self.config.get('CRAWL_DELAY', 1)
            }
        }
        
        return stats
    
    def test_crawlers(self) -> Dict[str, bool]:
        """测试所有爬虫是否正常工作"""
        test_results = {}
        test_query = "machine learning medical"
        
        for source, crawler in self.crawlers.items():
            try:
                papers = crawler.search_papers(test_query, max_results=1)
                test_results[source] = len(papers) > 0
                self.logger.info(f"{source} 爬虫测试: {'通过' if test_results[source] else '失败'}")
            except Exception as e:
                test_results[source] = False
                self.logger.error(f"{source} 爬虫测试失败: {e}")
        
        return test_results