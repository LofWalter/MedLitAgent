"""
Flask Web应用 - 医学文献爬取系统的Web界面和API
"""
import os
import sys
import logging
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import Config
from src.crawlers.crawler_manager import CrawlerManager
from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.text_classifier import MedicalTextClassifier
from src.database.database_manager import DatabaseManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__, 
           template_folder='../../templates',
           static_folder='../../static')
app.config['SECRET_KEY'] = 'medlit-secret-key'

# 启用CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化组件
try:
    config = Config.__dict__
    crawler_manager = CrawlerManager(config)
    keyword_extractor = KeywordExtractor(config)
    text_classifier = MedicalTextClassifier(config)
    db_manager = DatabaseManager(config.get('DATABASE_URL', 'sqlite:///medlit.db'))
    
    logger.info("系统组件初始化成功")
except Exception as e:
    logger.error(f"系统初始化失败: {e}")
    raise

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@app.route('/search')
def search_page():
    """搜索页面"""
    return render_template('search.html')

@app.route('/crawl')
def crawl_page():
    """爬取页面"""
    return render_template('crawl.html')

# API路由
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取系统统计信息"""
    try:
        stats = db_manager.get_statistics()
        crawler_stats = crawler_manager.get_crawler_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'database': stats,
                'crawlers': crawler_stats
            }
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取医学分类列表"""
    try:
        categories = db_manager.get_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        logger.error(f"获取分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    """开始爬取任务"""
    try:
        data = request.get_json()
        
        # 验证输入
        if not data:
            return jsonify({'success': False, 'error': '缺少请求数据'}), 400
        
        keywords = data.get('keywords', [])
        sources = data.get('sources', ['pubmed', 'arxiv'])
        max_results = data.get('max_results', 100)
        
        if not keywords:
            return jsonify({'success': False, 'error': '请提供关键词'}), 400
        
        logger.info(f"开始爬取任务: 关键词={keywords}, 数据源={sources}")
        
        # 执行爬取
        crawl_results = crawler_manager.crawl_by_keywords(
            keywords=keywords,
            sources=sources,
            max_results_per_keyword=max_results
        )
        
        # 处理爬取结果
        all_papers = []
        for source, papers in crawl_results.items():
            all_papers.extend(papers)
        
        # 提取关键词和分类
        if all_papers:
            logger.info("开始提取关键词和分类")
            papers_with_keywords = keyword_extractor.batch_extract_keywords(all_papers)
            
            # 训练分类器（如果需要）
            if not text_classifier.is_trained:
                logger.info("训练文本分类器")
                text_classifier.train()
            
            # 分类论文
            papers_with_classification = text_classifier.classify_papers(papers_with_keywords)
            
            # 保存到数据库
            logger.info("保存论文到数据库")
            save_results = db_manager.batch_save_papers(papers_with_classification)
            
            # 保存爬取会话
            session_data = {
                'session_name': f"Crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'query': json.dumps(keywords),
                'sources': sources,
                'total_papers': len(all_papers),
                'successful_papers': save_results['saved'],
                'failed_papers': save_results['failed'],
                'status': 'completed',
                'completed_at': datetime.utcnow(),
                'config': data
            }
            session_id = db_manager.save_crawl_session(session_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'session_id': session_id,
                    'total_papers': len(all_papers),
                    'saved_papers': save_results['saved'],
                    'failed_papers': save_results['failed'],
                    'skipped_papers': save_results['skipped'],
                    'sources': list(crawl_results.keys())
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'total_papers': 0,
                    'message': '未找到匹配的论文'
                }
            })
            
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/papers', methods=['GET'])
def search_papers():
    """搜索论文"""
    try:
        # 获取查询参数
        query = request.args.get('query', '')
        category = request.args.get('category', '')
        source = request.args.get('source', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 搜索论文
        papers = db_manager.search_papers(
            query=query if query else None,
            category=category if category else None,
            source=source if source else None,
            limit=per_page,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': {
                'papers': papers,
                'page': page,
                'per_page': per_page,
                'total': len(papers)  # 简化版本，实际应该查询总数
            }
        })
        
    except Exception as e:
        logger.error(f"搜索论文失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/papers/<int:paper_id>', methods=['GET'])
def get_paper_detail(paper_id):
    """获取论文详情"""
    try:
        paper = db_manager.get_paper_by_id(paper_id)
        if paper:
            return jsonify({
                'success': True,
                'data': paper
            })
        else:
            return jsonify({'success': False, 'error': '论文不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取论文详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extract-keywords', methods=['POST'])
def extract_keywords():
    """提取文本关键词"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': '请提供文本'}), 400
        
        result = keyword_extractor.extract_and_classify(text)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"关键词提取失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classify-text', methods=['POST'])
def classify_text():
    """分类文本"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': '请提供文本'}), 400
        
        # 确保分类器已训练
        if not text_classifier.is_trained:
            # 尝试加载已保存的模型
            if not text_classifier.load_model():
                # 如果没有保存的模型，进行训练
                train_result = text_classifier.train()
                if not train_result['success']:
                    return jsonify({'success': False, 'error': '分类器训练失败'}), 500
        
        result = text_classifier.classify_text(text)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"文本分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-crawlers', methods=['GET'])
def test_crawlers():
    """测试爬虫"""
    try:
        test_results = crawler_manager.test_crawlers()
        return jsonify({
            'success': True,
            'data': test_results
        })
    except Exception as e:
        logger.error(f"测试爬虫失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_papers():
    """导出论文数据"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'csv')  # csv, excel, json
        filters = data.get('filters', {})
        
        # 获取要导出的论文
        papers = db_manager.search_papers(
            query=filters.get('query'),
            category=filters.get('category'),
            source=filters.get('source'),
            limit=filters.get('limit', 1000)
        )
        
        if not papers:
            return jsonify({'success': False, 'error': '没有找到要导出的论文'}), 400
        
        # 生成导出文件
        from src.utils.export_utils import ExportUtils
        export_utils = ExportUtils()
        
        if export_format == 'csv':
            file_path = export_utils.export_to_csv(papers)
        elif export_format == 'excel':
            file_path = export_utils.export_to_excel(papers)
        elif export_format == 'json':
            file_path = export_utils.export_to_json(papers)
        else:
            return jsonify({'success': False, 'error': '不支持的导出格式'}), 400
        
        # 记录导出
        export_record = {
            'export_type': export_format,
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'query_filters': filters,
            'paper_count': len(papers),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"导出失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'success': False, 'error': '页面不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(Config.PAPERS_DIR, exist_ok=True)
    os.makedirs(Config.KEYWORDS_DIR, exist_ok=True)
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    
    # 启动应用
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )