"""
PubMed爬虫 - 爬取PubMed数据库的医学文献
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from .base_crawler import BaseCrawler
import re
from datetime import datetime

class PubMedCrawler(BaseCrawler):
    """PubMed数据库爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['DATA_SOURCES']['pubmed']['base_url']
        self.api_key = config.get('PUBMED_API_KEY', '')
        self.email = config.get('PUBMED_EMAIL', '')
        
    def search_papers(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索PubMed论文"""
        if max_results is None:
            max_results = self.max_papers
            
        # 第一步：搜索获取PMID列表
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
            
        try:
            response = self._make_request(search_url, params=search_params)
            search_data = response.json()
            
            pmids = search_data.get('esearchresult', {}).get('idlist', [])
            if not pmids:
                self.logger.warning(f"未找到匹配查询 '{query}' 的论文")
                return []
            
            self.logger.info(f"找到 {len(pmids)} 个PMID")
            
            # 第二步：批量获取论文详细信息
            papers = []
            batch_size = 200  # PubMed API建议的批次大小
            
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                batch_papers = self._fetch_paper_details_batch(batch_pmids)
                papers.extend(batch_papers)
                
            return papers
            
        except Exception as e:
            self.logger.error(f"搜索PubMed时出错: {e}")
            return []
    
    def _fetch_paper_details_batch(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """批量获取论文详细信息"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        if self.api_key:
            fetch_params['api_key'] = self.api_key
        if self.email:
            fetch_params['email'] = self.email
            
        try:
            response = self._make_request(fetch_url, params=fetch_params)
            return self._parse_pubmed_xml(response.text)
        except Exception as e:
            self.logger.error(f"获取论文详情时出错: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """解析PubMed XML响应"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper_data = self._extract_paper_info(article)
                if paper_data:
                    papers.append(self.normalize_paper_data(paper_data))
                    
        except ET.ParseError as e:
            self.logger.error(f"XML解析错误: {e}")
            
        return papers
    
    def _extract_paper_info(self, article_elem) -> Optional[Dict[str, Any]]:
        """从XML元素中提取论文信息"""
        try:
            # PMID
            pmid_elem = article_elem.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else ''
            
            # 标题
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''
            
            # 摘要
            abstract_parts = []
            for abstract_elem in article_elem.findall('.//AbstractText'):
                if abstract_elem.text:
                    label = abstract_elem.get('Label', '')
                    text = abstract_elem.text
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
            abstract = ' '.join(abstract_parts)
            
            # 作者
            authors = []
            for author_elem in article_elem.findall('.//Author'):
                last_name = author_elem.find('LastName')
                first_name = author_elem.find('ForeName')
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
            
            # 期刊
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ''
            
            # 发表日期
            pub_date = self._extract_publication_date(article_elem)
            
            # DOI
            doi = ''
            for article_id in article_elem.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            # 关键词
            keywords = []
            for keyword_elem in article_elem.findall('.//Keyword'):
                if keyword_elem.text:
                    keywords.append(keyword_elem.text)
            
            # MeSH术语作为关键词
            for mesh_elem in article_elem.findall('.//MeshHeading/DescriptorName'):
                if mesh_elem.text:
                    keywords.append(mesh_elem.text)
            
            return {
                'id': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal,
                'publication_date': pub_date,
                'doi': doi,
                'keywords': keywords,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ''
            }
            
        except Exception as e:
            self.logger.error(f"提取论文信息时出错: {e}")
            return None
    
    def _extract_publication_date(self, article_elem) -> str:
        """提取发表日期"""
        # 尝试多种日期格式
        date_paths = [
            './/PubDate',
            './/ArticleDate',
            './/DateCompleted'
        ]
        
        for path in date_paths:
            date_elem = article_elem.find(path)
            if date_elem is not None:
                year_elem = date_elem.find('Year')
                month_elem = date_elem.find('Month')
                day_elem = date_elem.find('Day')
                
                if year_elem is not None:
                    year = year_elem.text
                    month = month_elem.text if month_elem is not None else '01'
                    day = day_elem.text if day_elem is not None else '01'
                    
                    # 处理月份名称
                    month_names = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    if month in month_names:
                        month = month_names[month]
                    
                    try:
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except:
                        return year
        
        return ''
    
    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """获取单篇论文的详细信息"""
        papers = self._fetch_paper_details_batch([paper_id])
        return papers[0] if papers else {}
    
    def search_by_medical_category(self, category: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """根据医学分类搜索"""
        # 构建更精确的搜索查询
        category_queries = {
            'cardiology': 'cardiology[MeSH] OR cardiovascular[MeSH] OR heart disease[MeSH]',
            'oncology': 'neoplasms[MeSH] OR cancer[MeSH] OR tumor[MeSH]',
            'neurology': 'neurology[MeSH] OR nervous system diseases[MeSH]',
            'immunology': 'immunology[MeSH] OR immune system[MeSH]',
            'pharmacology': 'pharmacology[MeSH] OR drug therapy[MeSH]',
            'genetics': 'genetics[MeSH] OR genomics[MeSH]',
            'infectious_diseases': 'communicable diseases[MeSH] OR infection[MeSH]',
            'surgery': 'surgery[MeSH] OR surgical procedures[MeSH]',
            'pediatrics': 'pediatrics[MeSH] OR child[MeSH]',
            'psychiatry': 'psychiatry[MeSH] OR mental disorders[MeSH]'
        }
        
        query = category_queries.get(category, category)
        return self.search_papers(query, max_results)