#!/usr/bin/env python3
"""
MedLitAgent - 医学文献爬取和整理系统
主程序入口
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config.config import Config
from src.crawlers.crawler_manager import CrawlerManager
from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.text_classifier import MedicalTextClassifier
from src.database.database_manager import DatabaseManager
from src.utils.export_utils import ExportUtils

def setup_logging():
    """设置日志"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"medlit_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def init_system():
    """初始化系统组件"""
    print("正在初始化系统组件...")
    
    # 创建必要的目录
    directories = [
        Config.DATA_DIR,
        Config.PAPERS_DIR,
        Config.KEYWORDS_DIR,
        Config.REPORTS_DIR,
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # 初始化组件
    config = Config.__dict__
    
    crawler_manager = CrawlerManager(config)
    keyword_extractor = KeywordExtractor(config)
    text_classifier = MedicalTextClassifier(config)
    db_manager = DatabaseManager(config.get('DATABASE_URL', 'sqlite:///medlit.db'))
    export_utils = ExportUtils()
    
    print("系统组件初始化完成!")
    
    return {
        'crawler_manager': crawler_manager,
        'keyword_extractor': keyword_extractor,
        'text_classifier': text_classifier,
        'db_manager': db_manager,
        'export_utils': export_utils
    }

def crawl_command(args, components):
    """执行爬取命令"""
    print(f"开始爬取任务...")
    print(f"关键词: {args.keywords}")
    print(f"数据源: {args.sources}")
    print(f"最大结果数: {args.max_results}")
    
    crawler_manager = components['crawler_manager']
    keyword_extractor = components['keyword_extractor']
    text_classifier = components['text_classifier']
    db_manager = components['db_manager']
    
    # 执行爬取
    results = crawler_manager.crawl_by_keywords(
        keywords=args.keywords,
        sources=args.sources,
        max_results_per_keyword=args.max_results
    )
    
    # 合并所有论文
    all_papers = []
    for source, papers in results.items():
        all_papers.extend(papers)
    
    print(f"爬取完成，共获得 {len(all_papers)} 篇论文")
    
    if all_papers:
        # 提取关键词
        print("正在提取关键词...")
        papers_with_keywords = keyword_extractor.batch_extract_keywords(all_papers)
        
        # 训练和分类
        print("正在训练分类器...")
        if not text_classifier.is_trained:
            text_classifier.train()
        
        print("正在分类论文...")
        papers_with_classification = text_classifier.classify_papers(papers_with_keywords)
        
        # 保存到数据库
        print("正在保存到数据库...")
        save_results = db_manager.batch_save_papers(papers_with_classification)
        
        print(f"保存完成: 成功 {save_results['saved']}, 跳过 {save_results['skipped']}, 失败 {save_results['failed']}")
        
        # 如果指定了输出文件，则导出
        if args.output:
            export_utils = components['export_utils']
            if args.output.endswith('.csv'):
                export_utils.export_to_csv(papers_with_classification, args.output)
            elif args.output.endswith('.xlsx'):
                export_utils.export_to_excel(papers_with_classification, args.output)
            elif args.output.endswith('.json'):
                export_utils.export_to_json(papers_with_classification, args.output)
            print(f"结果已导出到: {args.output}")

def search_command(args, components):
    """执行搜索命令"""
    db_manager = components['db_manager']
    
    papers = db_manager.search_papers(
        query=args.query,
        category=args.category,
        source=args.source,
        limit=args.limit
    )
    
    print(f"找到 {len(papers)} 篇论文:")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   作者: {', '.join(paper.get('authors', [])[:3])}")
        print(f"   期刊: {paper.get('journal', 'N/A')}")
        print(f"   分类: {paper.get('predicted_category', 'N/A')}")
        print()

def export_command(args, components):
    """执行导出命令"""
    db_manager = components['db_manager']
    export_utils = components['export_utils']
    
    # 搜索要导出的论文
    papers = db_manager.search_papers(
        query=args.query,
        category=args.category,
        source=args.source,
        limit=args.limit or 10000
    )
    
    if not papers:
        print("没有找到要导出的论文")
        return
    
    print(f"准备导出 {len(papers)} 篇论文...")
    
    # 根据格式导出
    if args.format == 'csv':
        filepath = export_utils.export_to_csv(papers, args.output)
    elif args.format == 'excel':
        filepath = export_utils.export_to_excel(papers, args.output)
    elif args.format == 'json':
        filepath = export_utils.export_to_json(papers, args.output)
    elif args.format == 'pdf':
        filepath = export_utils.export_to_pdf(papers, args.output)
    elif args.format == 'report':
        filepath = export_utils.export_summary_report(papers, args.output)
    else:
        print(f"不支持的导出格式: {args.format}")
        return
    
    print(f"导出完成: {filepath}")

def stats_command(args, components):
    """显示统计信息"""
    db_manager = components['db_manager']
    
    stats = db_manager.get_statistics()
    
    print("=== 系统统计信息 ===")
    print(f"总论文数: {stats.get('total_papers', 0)}")
    print(f"总关键词数: {stats.get('total_keywords', 0)}")
    print(f"近7天新增: {stats.get('recent_papers_7days', 0)}")
    
    print("\n数据源分布:")
    for source, count in stats.get('source_distribution', {}).items():
        print(f"  {source}: {count}")
    
    print("\n分类分布:")
    for category, count in stats.get('category_distribution', {}).items():
        print(f"  {category}: {count}")

def web_command(args, components):
    """启动Web服务"""
    host = args.host
    port = args.port
    debug = args.debug or Config.FLASK_DEBUG
    
    print("正在启动Web服务...")
    print(f"访问地址: http://{host}:{port}")
    
    # 导入并启动Flask应用
    from src.api.app import app
    app.run(
        host=host,
        port=port,
        debug=debug
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MedLitAgent - 医学文献爬取和整理系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 爬取命令
    crawl_parser = subparsers.add_parser('crawl', help='爬取文献')
    crawl_parser.add_argument('keywords', nargs='+', help='搜索关键词')
    crawl_parser.add_argument('--sources', nargs='+', default=['pubmed', 'arxiv'], 
                             choices=['pubmed', 'arxiv'], help='数据源')
    crawl_parser.add_argument('--max-results', type=int, default=100, help='每个关键词最大结果数')
    crawl_parser.add_argument('--output', help='输出文件路径')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索文献')
    search_parser.add_argument('--query', help='搜索查询')
    search_parser.add_argument('--category', help='分类过滤')
    search_parser.add_argument('--source', help='数据源过滤')
    search_parser.add_argument('--limit', type=int, default=20, help='结果数量限制')
    
    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出文献')
    export_parser.add_argument('--format', choices=['csv', 'excel', 'json', 'pdf', 'report'], 
                              default='csv', help='导出格式')
    export_parser.add_argument('--query', help='搜索查询')
    export_parser.add_argument('--category', help='分类过滤')
    export_parser.add_argument('--source', help='数据源过滤')
    export_parser.add_argument('--limit', type=int, help='结果数量限制')
    export_parser.add_argument('--output', help='输出文件名')
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    # Web服务命令
    web_parser = subparsers.add_parser('web', help='启动Web服务')
    web_parser.add_argument('--host', default=Config.FLASK_HOST, help='服务器主机地址')
    web_parser.add_argument('--port', type=int, default=Config.FLASK_PORT, help='服务器端口')
    web_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 设置日志
    setup_logging()
    
    # 初始化系统
    try:
        components = init_system()
    except Exception as e:
        print(f"系统初始化失败: {e}")
        return
    
    # 执行命令
    try:
        if args.command == 'crawl':
            crawl_command(args, components)
        elif args.command == 'search':
            search_command(args, components)
        elif args.command == 'export':
            export_command(args, components)
        elif args.command == 'stats':
            stats_command(args, components)
        elif args.command == 'web':
            web_command(args, components)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"执行命令时出错: {e}")
        logging.exception("命令执行异常")

if __name__ == '__main__':
    main()