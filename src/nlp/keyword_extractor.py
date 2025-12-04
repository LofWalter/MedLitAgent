"""
关键词提取器 - 从医学文献中提取关键词
"""
import re
import json
import logging
from typing import List, Dict, Any, Set, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

class KeywordExtractor:
    """医学文献关键词提取器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化NLTK
        self._init_nltk()
        
        # 初始化spaCy
        self._init_spacy()
        
        # 加载医学关键词词典
        self.medical_keywords = self._load_medical_keywords()
        
        # 医学术语模式
        self.medical_patterns = self._compile_medical_patterns()
        
    def _init_nltk(self):
        """初始化NLTK资源"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def _init_spacy(self):
        """初始化spaCy模型"""
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy未安装，将使用基础NLP功能")
            self.nlp = None
            return
            
        try:
            self.nlp = spacy.load(self.config.get('SPACY_MODEL', 'en_core_web_sm'))
        except OSError:
            self.logger.warning("spaCy模型未找到，将使用基础NLP功能")
            self.nlp = None
    
    def _load_medical_keywords(self) -> Dict[str, List[str]]:
        """加载医学关键词词典"""
        try:
            keywords_file = self.config.get('MEDICAL_KEYWORDS_FILE', 'config/medical_keywords.json')
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载医学关键词失败: {e}")
            return {}
    
    def _compile_medical_patterns(self) -> List[re.Pattern]:
        """编译医学术语正则表达式模式"""
        patterns = [
            # 药物名称模式
            re.compile(r'\b[A-Z][a-z]+(?:mab|nib|pril|sartan|statin|mycin|cillin)\b'),
            # 疾病名称模式
            re.compile(r'\b(?:syndrome|disease|disorder|condition|cancer|tumor|carcinoma)\b', re.IGNORECASE),
            # 医学程序模式
            re.compile(r'\b(?:therapy|treatment|surgery|procedure|intervention|diagnosis)\b', re.IGNORECASE),
            # 解剖结构模式
            re.compile(r'\b(?:heart|brain|liver|kidney|lung|bone|muscle|nerve|blood)\b', re.IGNORECASE),
            # 医学测量模式
            re.compile(r'\b\d+\s*(?:mg|ml|cm|mm|kg|g|%|units?)\b'),
            # 基因/蛋白质模式
            re.compile(r'\b[A-Z]{2,}[0-9]+\b'),
        ]
        return patterns
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """从文本中提取关键词"""
        if not text:
            return []
        
        # 多种方法提取关键词
        keywords = []
        
        # 1. 基于词典的提取
        dict_keywords = self._extract_dictionary_keywords(text)
        keywords.extend(dict_keywords)
        
        # 2. 基于模式的提取
        pattern_keywords = self._extract_pattern_keywords(text)
        keywords.extend(pattern_keywords)
        
        # 3. 基于TF-IDF的提取
        tfidf_keywords = self._extract_tfidf_keywords(text)
        keywords.extend(tfidf_keywords)
        
        # 4. 基于spaCy的命名实体识别
        if self.nlp:
            ner_keywords = self._extract_ner_keywords(text)
            keywords.extend(ner_keywords)
        
        # 合并和排序关键词
        merged_keywords = self._merge_and_rank_keywords(keywords)
        
        return merged_keywords[:max_keywords]
    
    def _extract_dictionary_keywords(self, text: str) -> List[Dict[str, Any]]:
        """基于医学词典提取关键词"""
        keywords = []
        text_lower = text.lower()
        
        for category, terms in self.medical_keywords.items():
            for term in terms:
                if term.lower() in text_lower:
                    # 计算词频
                    count = text_lower.count(term.lower())
                    keywords.append({
                        'keyword': term,
                        'category': category,
                        'score': count * 2.0,  # 词典匹配给予更高权重
                        'method': 'dictionary'
                    })
        
        return keywords
    
    def _extract_pattern_keywords(self, text: str) -> List[Dict[str, Any]]:
        """基于正则表达式模式提取关键词"""
        keywords = []
        
        for pattern in self.medical_patterns:
            matches = pattern.findall(text)
            for match in matches:
                keywords.append({
                    'keyword': match,
                    'category': 'pattern_match',
                    'score': 1.5,
                    'method': 'pattern'
                })
        
        return keywords
    
    def _extract_tfidf_keywords(self, text: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """基于TF-IDF提取关键词"""
        # 简化的TF-IDF实现
        sentences = sent_tokenize(text)
        
        # 分词和预处理
        all_words = []
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            # 过滤停用词和非字母词
            words = [self.lemmatizer.lemmatize(word) for word in words 
                    if word.isalpha() and word not in self.stop_words and len(word) > 2]
            all_words.extend(words)
        
        # 计算词频
        word_freq = Counter(all_words)
        
        # 简单的TF-IDF计算（这里简化为TF * log(总词数/词频)）
        total_words = len(all_words)
        keywords = []
        
        for word, freq in word_freq.most_common(top_n):
            if freq > 1:  # 至少出现2次
                tf_idf_score = freq * (total_words / freq) / 100  # 归一化
                keywords.append({
                    'keyword': word,
                    'category': 'tfidf',
                    'score': tf_idf_score,
                    'method': 'tfidf'
                })
        
        return keywords
    
    def _extract_ner_keywords(self, text: str) -> List[Dict[str, Any]]:
        """基于命名实体识别提取关键词"""
        if not self.nlp:
            return []
        
        keywords = []
        doc = self.nlp(text)
        
        # 提取命名实体
        for ent in doc.ents:
            # 关注医学相关的实体类型
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                keywords.append({
                    'keyword': ent.text,
                    'category': f'ner_{ent.label_.lower()}',
                    'score': 1.0,
                    'method': 'ner'
                })
        
        # 提取名词短语
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2 and len(chunk.text) > 5:
                keywords.append({
                    'keyword': chunk.text,
                    'category': 'noun_phrase',
                    'score': 0.8,
                    'method': 'ner'
                })
        
        return keywords
    
    def _merge_and_rank_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并重复关键词并排序"""
        keyword_dict = {}
        
        for kw in keywords:
            key = kw['keyword'].lower().strip()
            if key in keyword_dict:
                # 合并分数
                keyword_dict[key]['score'] += kw['score']
                # 合并方法
                if kw['method'] not in keyword_dict[key]['methods']:
                    keyword_dict[key]['methods'].append(kw['method'])
            else:
                keyword_dict[key] = {
                    'keyword': kw['keyword'],
                    'category': kw['category'],
                    'score': kw['score'],
                    'methods': [kw['method']]
                }
        
        # 按分数排序
        sorted_keywords = sorted(keyword_dict.values(), 
                               key=lambda x: x['score'], reverse=True)
        
        return sorted_keywords
    
    def classify_keywords(self, keywords: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """将关键词按医学分类进行分组"""
        classified = {}
        
        # 初始化分类
        for category in self.medical_keywords.keys():
            classified[category] = []
        
        classified['other'] = []
        
        for kw in keywords:
            # 检查是否属于已知医学分类
            assigned = False
            keyword_lower = kw['keyword'].lower()
            
            for category, terms in self.medical_keywords.items():
                for term in terms:
                    if term.lower() in keyword_lower or keyword_lower in term.lower():
                        classified[category].append(kw)
                        assigned = True
                        break
                if assigned:
                    break
            
            if not assigned:
                classified['other'].append(kw)
        
        # 移除空分类
        classified = {k: v for k, v in classified.items() if v}
        
        return classified
    
    def extract_and_classify(self, text: str, max_keywords: int = 20) -> Dict[str, Any]:
        """提取并分类关键词"""
        keywords = self.extract_keywords(text, max_keywords)
        classified = self.classify_keywords(keywords)
        
        return {
            'total_keywords': len(keywords),
            'all_keywords': keywords,
            'classified_keywords': classified,
            'categories_found': list(classified.keys())
        }
    
    def batch_extract_keywords(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量提取论文关键词"""
        results = []
        
        for paper in papers:
            # 合并标题和摘要
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            
            # 提取关键词
            keyword_result = self.extract_and_classify(text)
            
            # 添加到论文数据中
            paper_with_keywords = paper.copy()
            paper_with_keywords.update({
                'extracted_keywords': keyword_result['all_keywords'],
                'classified_keywords': keyword_result['classified_keywords'],
                'keyword_categories': keyword_result['categories_found']
            })
            
            results.append(paper_with_keywords)
        
        return results