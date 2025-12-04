"""
arXiv爬虫 - 爬取arXiv上的医学相关论文
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from .base_crawler import BaseCrawler
import re
from datetime import datetime

class ArxivCrawler(BaseCrawler):
    """arXiv数据库爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['DATA_SOURCES']['arxiv']['base_url']
        self.categories = config['DATA_SOURCES']['arxiv']['categories']
        
    def search_papers(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索arXiv论文"""
        if max_results is None:
            max_results = self.max_papers
            
        # 构建搜索查询，限制在医学相关分类
        search_query = self._build_medical_query(query)
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = self._make_request(self.base_url, params=params)
            return self._parse_arxiv_xml(response.text)
        except Exception as e:
            self.logger.error(f"搜索arXiv时出错: {e}")
            return []
    
    def _build_medical_query(self, query: str) -> str:
        """构建医学相关的搜索查询"""
        # 在医学相关分类中搜索
        category_filter = ' OR '.join([f'cat:{cat}' for cat in self.categories])
        
        # 组合查询和分类过滤
        if query:
            return f"({query}) AND ({category_filter})"
        else:
            return category_filter
    
    def _parse_arxiv_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """解析arXiv XML响应"""
        papers = []
        
        try:
            # 处理命名空间
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            root = ET.fromstring(xml_content)
            
            for entry in root.findall('atom:entry', namespaces):
                paper_data = self._extract_paper_info(entry, namespaces)
                if paper_data:
                    papers.append(self.normalize_paper_data(paper_data))
                    
        except ET.ParseError as e:
            self.logger.error(f"XML解析错误: {e}")
            
        return papers
    
    def _extract_paper_info(self, entry_elem, namespaces: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """从XML元素中提取论文信息"""
        try:
            # arXiv ID
            id_elem = entry_elem.find('atom:id', namespaces)
            arxiv_id = ''
            if id_elem is not None:
                arxiv_id = id_elem.text.split('/')[-1]  # 提取ID部分
            
            # 标题
            title_elem = entry_elem.find('atom:title', namespaces)
            title = title_elem.text.strip() if title_elem is not None else ''
            
            # 摘要
            summary_elem = entry_elem.find('atom:summary', namespaces)
            abstract = summary_elem.text.strip() if summary_elem is not None else ''
            
            # 作者
            authors = []
            for author_elem in entry_elem.findall('atom:author', namespaces):
                name_elem = author_elem.find('atom:name', namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # 发表日期
            published_elem = entry_elem.find('atom:published', namespaces)
            publication_date = ''
            if published_elem is not None:
                # 格式: 2023-01-15T09:30:00Z
                date_str = published_elem.text
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    publication_date = dt.strftime('%Y-%m-%d')
                except:
                    publication_date = date_str[:10]  # 取前10个字符作为日期
            
            # 分类
            categories = []
            for category_elem in entry_elem.findall('arxiv:primary_category', namespaces):
                term = category_elem.get('term')
                if term:
                    categories.append(term)
            
            for category_elem in entry_elem.findall('atom:category', namespaces):
                term = category_elem.get('term')
                if term and term not in categories:
                    categories.append(term)
            
            # DOI (如果有)
            doi = ''
            for link_elem in entry_elem.findall('atom:link', namespaces):
                if link_elem.get('title') == 'doi':
                    doi = link_elem.get('href', '').replace('http://dx.doi.org/', '')
                    break
            
            # URL
            url = ''
            for link_elem in entry_elem.findall('atom:link', namespaces):
                if link_elem.get('rel') == 'alternate':
                    url = link_elem.get('href', '')
                    break
            
            # 从摘要中提取关键词（简单方法）
            keywords = self._extract_keywords_from_text(title + ' ' + abstract)
            
            return {
                'id': arxiv_id,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': 'arXiv',
                'publication_date': publication_date,
                'doi': doi,
                'keywords': keywords,
                'categories': categories,
                'url': url
            }
            
        except Exception as e:
            self.logger.error(f"提取论文信息时出错: {e}")
            return None
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取，基于医学术语
        medical_terms = [
            'algorithm', 'machine learning', 'deep learning', 'neural network',
            'medical', 'clinical', 'diagnosis', 'treatment', 'therapy',
            'patient', 'disease', 'cancer', 'tumor', 'imaging', 'MRI', 'CT',
            'ultrasound', 'X-ray', 'segmentation', 'classification', 'detection',
            'prediction', 'analysis', 'biomedical', 'healthcare', 'medicine'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for term in medical_terms:
            if term in text_lower:
                found_keywords.append(term)
        
        return found_keywords[:10]  # 限制关键词数量
    
    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """获取单篇论文的详细信息"""
        # arXiv ID格式处理
        if not paper_id.startswith('http'):
            paper_id = f"http://arxiv.org/abs/{paper_id}"
        
        params = {
            'id_list': paper_id.split('/')[-1],  # 提取ID
            'max_results': 1
        }
        
        try:
            response = self._make_request(self.base_url, params=params)
            papers = self._parse_arxiv_xml(response.text)
            return papers[0] if papers else {}
        except Exception as e:
            self.logger.error(f"获取arXiv论文详情时出错: {e}")
            return {}
    
    def search_by_category(self, category: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """根据arXiv分类搜索"""
        params = {
            'search_query': f'cat:{category}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self._make_request(self.base_url, params=params)
            return self._parse_arxiv_xml(response.text)
        except Exception as e:
            self.logger.error(f"按分类搜索arXiv时出错: {e}")
            return []
    
    def search_recent_papers(self, days: int = 30, max_results: int = 100) -> List[Dict[str, Any]]:
        """搜索最近的医学相关论文"""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建日期范围查询
        date_query = f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
        category_filter = ' OR '.join([f'cat:{cat}' for cat in self.categories])
        
        search_query = f"({date_query}) AND ({category_filter})"
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self._make_request(self.base_url, params=params)
            return self._parse_arxiv_xml(response.text)
        except Exception as e:
            self.logger.error(f"搜索最近论文时出错: {e}")
            return []