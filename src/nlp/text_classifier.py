"""
文本分类器 - 对医学文献进行自动分类
"""
import logging
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import pickle
import os

class MedicalTextClassifier:
    """医学文献文本分类器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 医学分类标签
        self.medical_categories = config.get('MEDICAL_CATEGORIES', {})
        self.category_labels = list(self.medical_categories.keys())
        
        # 分类器组件
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        self.classifier = LogisticRegression(
            random_state=42,
            max_iter=1000,
            multi_class='ovr'
        )
        
        self.is_trained = False
        self.model_path = os.path.join(config.get('DATA_DIR', 'data'), 'models')
        os.makedirs(self.model_path, exist_ok=True)
    
    def preprocess_text(self, text: str) -> str:
        """预处理文本"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除特殊字符，保留字母、数字和空格
        import re
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        return text
    
    def create_training_data_from_keywords(self) -> Tuple[List[str], List[str]]:
        """基于关键词创建训练数据"""
        texts = []
        labels = []
        
        # 为每个医学分类创建训练样本
        for category, keywords in self.medical_categories.items():
            if isinstance(keywords, list):
                # 如果keywords是列表，使用它们
                category_keywords = keywords
            else:
                # 如果keywords是字符串（中文名称），使用预定义的英文关键词
                category_keywords = self._get_category_keywords(category)
            
            # 为每个关键词创建多个训练样本
            for keyword in category_keywords:
                # 创建包含关键词的句子
                sample_texts = [
                    f"This study focuses on {keyword} research and analysis.",
                    f"We investigated {keyword} in clinical settings.",
                    f"The {keyword} approach showed significant results.",
                    f"Novel {keyword} methods were developed.",
                    f"Patient outcomes improved with {keyword} treatment."
                ]
                
                for sample_text in sample_texts:
                    texts.append(sample_text)
                    labels.append(category)
        
        return texts, labels
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """获取分类的关键词"""
        # 预定义的医学分类关键词
        category_keywords = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'coronary', 'myocardial'],
            'oncology': ['cancer', 'tumor', 'malignant', 'chemotherapy', 'oncology'],
            'neurology': ['brain', 'neurological', 'stroke', 'epilepsy', 'neural'],
            'immunology': ['immune', 'immunology', 'antibody', 'antigen', 'vaccination'],
            'pharmacology': ['drug', 'medication', 'pharmaceutical', 'therapy', 'treatment'],
            'genetics': ['genetic', 'DNA', 'gene', 'genome', 'hereditary'],
            'infectious_diseases': ['infection', 'bacterial', 'viral', 'antibiotic', 'pathogen'],
            'surgery': ['surgery', 'surgical', 'operation', 'procedure', 'operative'],
            'pediatrics': ['pediatric', 'children', 'infant', 'child', 'adolescent'],
            'psychiatry': ['psychiatric', 'mental', 'depression', 'anxiety', 'psychological']
        }
        
        return category_keywords.get(category, [category])
    
    def train(self, papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """训练分类器"""
        if papers is None or len(papers) == 0:
            # 使用基于关键词的训练数据
            texts, labels = self.create_training_data_from_keywords()
            self.logger.info("使用基于关键词的训练数据")
        else:
            # 使用提供的论文数据
            texts, labels = self._prepare_training_data(papers)
            self.logger.info(f"使用 {len(papers)} 篇论文进行训练")
        
        if len(texts) == 0:
            self.logger.error("没有训练数据")
            return {'success': False, 'error': 'No training data'}
        
        try:
            # 预处理文本
            processed_texts = [self.preprocess_text(text) for text in texts]
            
            # 特征提取
            X = self.vectorizer.fit_transform(processed_texts)
            y = labels
            
            # 训练分类器
            self.classifier.fit(X, y)
            self.is_trained = True
            
            # 评估模型（如果有足够的数据）
            evaluation_results = {}
            if len(set(labels)) > 1 and len(texts) > 10:
                evaluation_results = self._evaluate_model(X, y)
            
            # 保存模型
            self.save_model()
            
            self.logger.info("分类器训练完成")
            
            return {
                'success': True,
                'training_samples': len(texts),
                'categories': len(set(labels)),
                'evaluation': evaluation_results
            }
            
        except Exception as e:
            self.logger.error(f"训练分类器时出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_training_data(self, papers: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """从论文数据准备训练数据"""
        texts = []
        labels = []
        
        for paper in papers:
            # 合并标题和摘要
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            
            # 尝试从关键词推断分类
            category = self._infer_category_from_keywords(paper)
            
            if category and text.strip():
                texts.append(text)
                labels.append(category)
        
        return texts, labels
    
    def _infer_category_from_keywords(self, paper: Dict[str, Any]) -> str:
        """从论文关键词推断分类"""
        # 获取论文的关键词
        keywords = paper.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # 合并标题和摘要中的词汇
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        
        # 计算每个分类的匹配分数
        category_scores = {}
        
        for category in self.category_labels:
            score = 0
            category_keywords = self._get_category_keywords(category)
            
            for keyword in category_keywords:
                if keyword.lower() in text:
                    score += 1
            
            # 检查论文关键词
            for paper_keyword in keywords:
                if isinstance(paper_keyword, str):
                    for category_keyword in category_keywords:
                        if category_keyword.lower() in paper_keyword.lower():
                            score += 2  # 关键词匹配给更高权重
            
            if score > 0:
                category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _evaluate_model(self, X, y) -> Dict[str, Any]:
        """评估模型性能"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 训练和预测
            self.classifier.fit(X_train, y_train)
            y_pred = self.classifier.predict(X_test)
            
            # 计算指标
            accuracy = accuracy_score(y_test, y_pred)
            
            return {
                'accuracy': accuracy,
                'test_samples': len(y_test),
                'categories_in_test': len(set(y_test))
            }
            
        except Exception as e:
            self.logger.error(f"模型评估时出错: {e}")
            return {}
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """分类单个文本"""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        try:
            # 预处理
            processed_text = self.preprocess_text(text)
            
            # 特征提取
            X = self.vectorizer.transform([processed_text])
            
            # 预测
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            
            # 获取所有分类的概率
            category_probs = {}
            for i, category in enumerate(self.classifier.classes_):
                category_probs[category] = float(probabilities[i])
            
            # 排序概率
            sorted_probs = sorted(category_probs.items(), 
                                key=lambda x: x[1], reverse=True)
            
            return {
                'predicted_category': prediction,
                'confidence': float(max(probabilities)),
                'all_probabilities': category_probs,
                'top_3_predictions': sorted_probs[:3]
            }
            
        except Exception as e:
            self.logger.error(f"文本分类时出错: {e}")
            return {'error': str(e)}
    
    def classify_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分类论文"""
        results = []
        
        for paper in papers:
            # 合并标题和摘要
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            
            # 分类
            classification_result = self.classify_text(text)
            
            # 添加分类结果到论文数据
            paper_with_classification = paper.copy()
            paper_with_classification['classification'] = classification_result
            
            results.append(paper_with_classification)
        
        return results
    
    def save_model(self):
        """保存训练好的模型"""
        try:
            # 保存向量化器
            vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # 保存分类器
            classifier_path = os.path.join(self.model_path, 'classifier.pkl')
            with open(classifier_path, 'wb') as f:
                pickle.dump(self.classifier, f)
            
            # 保存元数据
            metadata = {
                'categories': self.category_labels,
                'is_trained': self.is_trained,
                'model_type': 'LogisticRegression'
            }
            
            metadata_path = os.path.join(self.model_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"模型已保存到: {self.model_path}")
            
        except Exception as e:
            self.logger.error(f"保存模型时出错: {e}")
    
    def load_model(self) -> bool:
        """加载训练好的模型"""
        try:
            # 加载向量化器
            vectorizer_path = os.path.join(self.model_path, 'vectorizer.pkl')
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # 加载分类器
            classifier_path = os.path.join(self.model_path, 'classifier.pkl')
            with open(classifier_path, 'rb') as f:
                self.classifier = pickle.load(f)
            
            # 加载元数据
            metadata_path = os.path.join(self.model_path, 'metadata.json')
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            self.is_trained = metadata.get('is_trained', False)
            
            self.logger.info("模型加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"加载模型时出错: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'is_trained': self.is_trained,
            'categories': self.category_labels,
            'model_type': 'LogisticRegression',
            'vectorizer_features': getattr(self.vectorizer, 'max_features', None),
            'model_path': self.model_path
        }