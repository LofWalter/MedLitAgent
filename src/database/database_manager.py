"""
数据库管理器 - 处理所有数据库操作
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import create_engine, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .models import Base, Paper, Keyword, Category, PaperCategory, CrawlSession, SearchHistory, Export, SystemLog

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
        # 创建表
        self.create_tables()
        
        # 初始化医学分类
        self.init_categories()
    
    def create_tables(self):
        """创建数据库表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("数据库表创建成功")
        except Exception as e:
            self.logger.error(f"创建数据库表失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def init_categories(self):
        """初始化医学分类"""
        categories_data = [
            ('cardiology', '心脏病学', '心血管疾病的诊断和治疗'),
            ('oncology', '肿瘤学', '癌症和肿瘤的研究与治疗'),
            ('neurology', '神经学', '神经系统疾病的研究'),
            ('immunology', '免疫学', '免疫系统和免疫反应的研究'),
            ('pharmacology', '药理学', '药物作用机制和药物治疗'),
            ('genetics', '遗传学', '基因和遗传性疾病的研究'),
            ('infectious_diseases', '传染病学', '传染性疾病的预防和治疗'),
            ('surgery', '外科学', '外科手术和治疗方法'),
            ('pediatrics', '儿科学', '儿童疾病的诊断和治疗'),
            ('psychiatry', '精神病学', '精神疾病和心理健康'),
            ('radiology', '放射学', '医学影像和放射诊断'),
            ('pathology', '病理学', '疾病的病理机制研究'),
            ('epidemiology', '流行病学', '疾病分布和流行规律'),
            ('public_health', '公共卫生', '人群健康和疾病预防'),
            ('clinical_trials', '临床试验', '临床研究和药物试验')
        ]
        
        session = self.get_session()
        try:
            for name, display_name, description in categories_data:
                existing = session.query(Category).filter(Category.name == name).first()
                if not existing:
                    category = Category(
                        name=name,
                        display_name=display_name,
                        description=description
                    )
                    session.add(category)
            
            session.commit()
            self.logger.info("医学分类初始化完成")
        except Exception as e:
            session.rollback()
            self.logger.error(f"初始化医学分类失败: {e}")
        finally:
            session.close()
    
    def save_paper(self, paper_data: Dict[str, Any]) -> Optional[int]:
        """保存论文数据"""
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(Paper).filter(
                Paper.external_id == paper_data.get('id', '')
            ).first()
            
            if existing:
                self.logger.info(f"论文已存在: {paper_data.get('id', '')}")
                return existing.id
            
            # 创建新论文记录
            paper = Paper(
                external_id=paper_data.get('id', ''),
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract', ''),
                authors=paper_data.get('authors', []),
                journal=paper_data.get('journal', ''),
                publication_date=paper_data.get('publication_date', ''),
                doi=paper_data.get('doi', ''),
                url=paper_data.get('url', ''),
                source=paper_data.get('source', ''),
                original_keywords=paper_data.get('keywords', []),
                raw_data=paper_data
            )
            
            # 添加分类信息（如果有）
            classification = paper_data.get('classification', {})
            if classification:
                paper.predicted_category = classification.get('predicted_category')
                paper.classification_confidence = classification.get('confidence')
                paper.classification_probabilities = classification.get('all_probabilities')
            
            # 添加提取的关键词信息
            if 'extracted_keywords' in paper_data:
                paper.extracted_keywords = paper_data['extracted_keywords']
            if 'keyword_categories' in paper_data:
                paper.keyword_categories = paper_data['keyword_categories']
            
            session.add(paper)
            session.flush()  # 获取ID
            
            paper_id = paper.id
            
            # 保存关键词
            self._save_keywords(session, paper_id, paper_data)
            
            # 保存分类关联
            self._save_paper_categories(session, paper_id, paper_data)
            
            session.commit()
            self.logger.info(f"论文保存成功: {paper_data.get('title', '')[:50]}")
            return paper_id
            
        except IntegrityError as e:
            session.rollback()
            self.logger.warning(f"论文已存在或数据冲突: {e}")
            return None
        except Exception as e:
            session.rollback()
            self.logger.error(f"保存论文失败: {e}")
            return None
        finally:
            session.close()
    
    def _save_keywords(self, session: Session, paper_id: int, paper_data: Dict[str, Any]):
        """保存关键词"""
        # 保存提取的关键词
        extracted_keywords = paper_data.get('extracted_keywords', [])
        for kw_data in extracted_keywords:
            if isinstance(kw_data, dict):
                keyword = Keyword(
                    paper_id=paper_id,
                    keyword=kw_data.get('keyword', ''),
                    category=kw_data.get('category', ''),
                    score=kw_data.get('score', 0.0),
                    extraction_method=','.join(kw_data.get('methods', []))
                )
                session.add(keyword)
        
        # 保存原始关键词
        original_keywords = paper_data.get('keywords', [])
        for kw in original_keywords:
            if isinstance(kw, str) and kw.strip():
                keyword = Keyword(
                    paper_id=paper_id,
                    keyword=kw.strip(),
                    category='original',
                    score=1.0,
                    extraction_method='original'
                )
                session.add(keyword)
    
    def _save_paper_categories(self, session: Session, paper_id: int, paper_data: Dict[str, Any]):
        """保存论文分类关联"""
        classification = paper_data.get('classification', {})
        if not classification:
            return
        
        # 主要分类
        predicted_category = classification.get('predicted_category')
        if predicted_category:
            category = session.query(Category).filter(Category.name == predicted_category).first()
            if category:
                paper_category = PaperCategory(
                    paper_id=paper_id,
                    category_id=category.id,
                    confidence=classification.get('confidence', 0.0),
                    is_primary=True
                )
                session.add(paper_category)
        
        # 其他可能的分类
        all_probabilities = classification.get('all_probabilities', {})
        for cat_name, prob in all_probabilities.items():
            if cat_name != predicted_category and prob > 0.1:  # 只保存概率大于0.1的
                category = session.query(Category).filter(Category.name == cat_name).first()
                if category:
                    paper_category = PaperCategory(
                        paper_id=paper_id,
                        category_id=category.id,
                        confidence=prob,
                        is_primary=False
                    )
                    session.add(paper_category)
    
    def batch_save_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量保存论文"""
        results = {'saved': 0, 'skipped': 0, 'failed': 0}
        
        for paper_data in papers:
            paper_id = self.save_paper(paper_data)
            if paper_id:
                results['saved'] += 1
            elif paper_id is None:
                results['failed'] += 1
            else:
                results['skipped'] += 1
        
        self.logger.info(f"批量保存完成: {results}")
        return results
    
    def search_papers(self, query: str = None, category: str = None, 
                     source: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """搜索论文"""
        session = self.get_session()
        try:
            # 构建查询
            query_obj = session.query(Paper)
            
            # 添加搜索条件
            if query:
                query_obj = query_obj.filter(
                    or_(
                        Paper.title.contains(query),
                        Paper.abstract.contains(query)
                    )
                )
            
            if category:
                query_obj = query_obj.join(PaperCategory).join(Category).filter(
                    Category.name == category
                )
            
            if source:
                query_obj = query_obj.filter(Paper.source == source)
            
            # 排序和分页
            papers = query_obj.order_by(desc(Paper.created_at)).offset(offset).limit(limit).all()
            
            # 转换为字典格式
            results = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'external_id': paper.external_id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.authors,
                    'journal': paper.journal,
                    'publication_date': paper.publication_date,
                    'doi': paper.doi,
                    'url': paper.url,
                    'source': paper.source,
                    'predicted_category': paper.predicted_category,
                    'classification_confidence': paper.classification_confidence,
                    'created_at': paper.created_at.isoformat() if paper.created_at else None
                }
                results.append(paper_dict)
            
            return results
            
        except Exception as e:
            self.logger.error(f"搜索论文失败: {e}")
            return []
        finally:
            session.close()
    
    def get_paper_by_id(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取论文详情"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                return None
            
            # 获取关键词
            keywords = session.query(Keyword).filter(Keyword.paper_id == paper_id).all()
            
            # 获取分类
            categories = session.query(PaperCategory, Category).join(Category).filter(
                PaperCategory.paper_id == paper_id
            ).all()
            
            paper_dict = {
                'id': paper.id,
                'external_id': paper.external_id,
                'title': paper.title,
                'abstract': paper.abstract,
                'authors': paper.authors,
                'journal': paper.journal,
                'publication_date': paper.publication_date,
                'doi': paper.doi,
                'url': paper.url,
                'source': paper.source,
                'predicted_category': paper.predicted_category,
                'classification_confidence': paper.classification_confidence,
                'classification_probabilities': paper.classification_probabilities,
                'original_keywords': paper.original_keywords,
                'extracted_keywords': paper.extracted_keywords,
                'keyword_categories': paper.keyword_categories,
                'keywords': [
                    {
                        'keyword': kw.keyword,
                        'category': kw.category,
                        'score': kw.score,
                        'method': kw.extraction_method
                    } for kw in keywords
                ],
                'categories': [
                    {
                        'name': cat.name,
                        'display_name': cat.display_name,
                        'confidence': pc.confidence,
                        'is_primary': pc.is_primary
                    } for pc, cat in categories
                ],
                'created_at': paper.created_at.isoformat() if paper.created_at else None,
                'updated_at': paper.updated_at.isoformat() if paper.updated_at else None
            }
            
            return paper_dict
            
        except Exception as e:
            self.logger.error(f"获取论文详情失败: {e}")
            return None
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        session = self.get_session()
        try:
            # 基本统计
            total_papers = session.query(Paper).count()
            total_keywords = session.query(Keyword).count()
            
            # 按来源统计
            source_stats = session.query(
                Paper.source, func.count(Paper.id)
            ).group_by(Paper.source).all()
            
            # 按分类统计
            category_stats = session.query(
                Category.display_name, func.count(PaperCategory.id)
            ).join(PaperCategory).group_by(Category.id, Category.display_name).all()
            
            # 最近爬取统计
            from datetime import datetime, timedelta
            recent_date = datetime.utcnow() - timedelta(days=7)
            recent_papers = session.query(Paper).filter(
                Paper.created_at >= recent_date
            ).count()
            
            return {
                'total_papers': total_papers,
                'total_keywords': total_keywords,
                'recent_papers_7days': recent_papers,
                'source_distribution': dict(source_stats),
                'category_distribution': dict(category_stats)
            }
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            session.close()
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有医学分类"""
        session = self.get_session()
        try:
            categories = session.query(Category).all()
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'display_name': cat.display_name,
                    'description': cat.description
                } for cat in categories
            ]
        except Exception as e:
            self.logger.error(f"获取分类失败: {e}")
            return []
        finally:
            session.close()
    
    def save_crawl_session(self, session_data: Dict[str, Any]) -> int:
        """保存爬取会话"""
        session = self.get_session()
        try:
            crawl_session = CrawlSession(**session_data)
            session.add(crawl_session)
            session.commit()
            return crawl_session.id
        except Exception as e:
            session.rollback()
            self.logger.error(f"保存爬取会话失败: {e}")
            return 0
        finally:
            session.close()
    
    def log_system_event(self, level: str, module: str, message: str, details: Dict = None):
        """记录系统日志"""
        session = self.get_session()
        try:
            log_entry = SystemLog(
                level=level,
                module=module,
                message=message,
                details=details or {}
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"记录系统日志失败: {e}")
        finally:
            session.close()