#!/usr/bin/env python3
"""
MedLitAgent 演示脚本
展示系统的主要功能
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config.config import Config
from src.crawlers.crawler_manager import CrawlerManager
from src.nlp.keyword_extractor import KeywordExtractor
from src.nlp.text_classifier import MedicalTextClassifier
from src.database.database_manager import DatabaseManager

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def demo_keyword_extraction():
    """演示关键词提取功能"""
    print_header("关键词提取演示")
    
    # 初始化关键词提取器
    config = Config.__dict__
    extractor = KeywordExtractor(config)
    
    # 示例医学文本
    sample_text = """
    Machine learning approaches have shown great promise in medical image analysis, 
    particularly in the diagnosis of cardiovascular diseases. Deep learning models 
    can automatically detect patterns in cardiac MRI scans that may be missed by 
    human radiologists. This study presents a novel convolutional neural network 
    architecture for automated detection of myocardial infarction from 
    electrocardiogram signals. The proposed method achieved 95% accuracy on a 
    dataset of 10,000 patients with confirmed coronary artery disease.
    """
    
    print("示例文本:")
    print(sample_text.strip())
    print("\n提取的关键词:")
    
    # 提取关键词
    result = extractor.extract_and_classify(sample_text)
    
    print(f"总关键词数: {result['total_keywords']}")
    print(f"发现的分类: {', '.join(result['categories_found'])}")
    
    print("\n按分类整理的关键词:")
    for category, keywords in result['classified_keywords'].items():
        if keywords:
            print(f"\n{category}:")
            for kw in keywords[:5]:  # 只显示前5个
                print(f"  - {kw['keyword']} (分数: {kw['score']:.2f})")

def demo_text_classification():
    """演示文本分类功能"""
    print_header("文本分类演示")
    
    # 初始化分类器
    config = Config.__dict__
    classifier = MedicalTextClassifier(config)
    
    # 训练分类器
    print("正在训练分类器...")
    train_result = classifier.train()
    print(f"训练结果: {train_result}")
    
    # 示例文本
    test_texts = [
        "This study investigates the effectiveness of chemotherapy in treating lung cancer patients.",
        "A new surgical technique for cardiac bypass surgery shows promising results.",
        "Machine learning algorithms for analyzing brain MRI scans in Alzheimer's disease.",
        "Clinical trial results for a new antiviral drug against COVID-19.",
        "Genetic markers associated with hereditary breast cancer risk."
    ]
    
    print("\n分类结果:")
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. 文本: {text[:60]}...")
        result = classifier.classify_text(text)
        if 'predicted_category' in result:
            print(f"   预测分类: {result['predicted_category']}")
            print(f"   置信度: {result['confidence']:.3f}")

def demo_database_operations():
    """演示数据库操作"""
    print_header("数据库操作演示")
    
    # 初始化数据库管理器
    config = Config.__dict__
    db_manager = DatabaseManager(config.get('DATABASE_URL', 'sqlite:///demo.db'))
    
    # 示例论文数据
    sample_papers = [
        {
            'id': 'demo001',
            'title': 'Machine Learning in Medical Diagnosis',
            'abstract': 'This paper reviews the application of machine learning techniques in medical diagnosis.',
            'authors': ['John Smith', 'Jane Doe'],
            'journal': 'Journal of Medical AI',
            'publication_date': '2023-01-15',
            'doi': '10.1000/demo001',
            'url': 'https://example.com/demo001',
            'source': 'demo',
            'keywords': ['machine learning', 'medical diagnosis', 'artificial intelligence']
        },
        {
            'id': 'demo002',
            'title': 'Deep Learning for Cancer Detection',
            'abstract': 'A novel deep learning approach for early cancer detection using medical imaging.',
            'authors': ['Alice Johnson', 'Bob Wilson'],
            'journal': 'Cancer Research AI',
            'publication_date': '2023-02-20',
            'doi': '10.1000/demo002',
            'url': 'https://example.com/demo002',
            'source': 'demo',
            'keywords': ['deep learning', 'cancer detection', 'medical imaging']
        }
    ]
    
    print("保存示例论文到数据库...")
    save_results = db_manager.batch_save_papers(sample_papers)
    print(f"保存结果: {save_results}")
    
    print("\n搜索论文...")
    papers = db_manager.search_papers(query="machine learning", limit=5)
    print(f"找到 {len(papers)} 篇论文:")
    for paper in papers:
        print(f"  - {paper['title']}")
        print(f"    作者: {', '.join(paper.get('authors', []))}")
        print(f"    期刊: {paper.get('journal', 'N/A')}")
    
    print("\n数据库统计:")
    stats = db_manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

def demo_export_functionality():
    """演示导出功能"""
    print_header("导出功能演示")
    
    from src.utils.export_utils import ExportUtils
    
    # 示例数据
    sample_data = [
        {
            'id': 1,
            'title': 'AI in Healthcare',
            'authors': ['Dr. Smith', 'Dr. Johnson'],
            'journal': 'Medical AI Journal',
            'publication_date': '2023-01-01',
            'predicted_category': 'artificial_intelligence'
        },
        {
            'id': 2,
            'title': 'Cancer Treatment Advances',
            'authors': ['Dr. Brown', 'Dr. Davis'],
            'journal': 'Oncology Today',
            'publication_date': '2023-02-01',
            'predicted_category': 'oncology'
        }
    ]
    
    export_utils = ExportUtils('demo_exports')
    
    print("导出为CSV格式...")
    try:
        csv_file = export_utils.export_to_csv(sample_data, 'demo_papers.csv')
        print(f"CSV文件已保存: {csv_file}")
    except Exception as e:
        print(f"CSV导出失败: {e}")
    
    print("\n导出为JSON格式...")
    try:
        json_file = export_utils.export_to_json(sample_data, 'demo_papers.json')
        print(f"JSON文件已保存: {json_file}")
    except Exception as e:
        print(f"JSON导出失败: {e}")
    
    print("\n生成摘要报告...")
    try:
        report_file = export_utils.export_summary_report(sample_data, 'demo_report.html')
        print(f"摘要报告已保存: {report_file}")
    except Exception as e:
        print(f"报告生成失败: {e}")

def main():
    """主函数"""
    print_header("MedLitAgent 系统演示")
    print("这是一个医学文献爬取和整理系统的功能演示")
    print("系统包含以下主要功能:")
    print("1. 关键词提取和分类")
    print("2. 文本自动分类")
    print("3. 数据库存储和管理")
    print("4. 数据导出和报告生成")
    
    try:
        # 演示各个功能
        demo_keyword_extraction()
        demo_text_classification()
        demo_database_operations()
        demo_export_functionality()
        
        print_header("演示完成")
        print("所有功能演示已完成！")
        print("您可以使用以下命令来使用系统:")
        print("  python main.py crawl 'machine learning' --sources pubmed")
        print("  python main.py search --query 'cancer' --limit 10")
        print("  python main.py export --format csv --category oncology")
        print("  python main.py web  # 启动Web界面")
        
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()