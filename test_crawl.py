#!/usr/bin/env python3
"""
测试爬取功能的简单脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from src.crawlers.pubmed_crawler import PubMedCrawler
from src.crawlers.arxiv_crawler import ArxivCrawler

def test_pubmed_crawler():
    """测试PubMed爬虫"""
    print("测试PubMed爬虫...")
    
    config = {
        'DATA_SOURCES': {
            'pubmed': {
                'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
                'api_key': None,
                'email': 'test@example.com'
            }
        },
        'CRAWL_DELAY': 1,
        'MAX_PAPERS_PER_QUERY': 5
    }
    
    crawler = PubMedCrawler(config)
    
    try:
        # 测试搜索
        papers = crawler.search_papers("machine learning", max_results=3)
        print(f"PubMed搜索结果: {len(papers)} 篇论文")
        
        if papers:
            print("第一篇论文:")
            paper = papers[0]
            print(f"  标题: {paper.get('title', 'N/A')[:100]}...")
            print(f"  作者: {', '.join(paper.get('authors', [])[:3])}")
            print(f"  期刊: {paper.get('journal', 'N/A')}")
            print(f"  发表日期: {paper.get('publication_date', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"PubMed爬虫测试失败: {e}")
        return False

def test_arxiv_crawler():
    """测试arXiv爬虫"""
    print("\n测试arXiv爬虫...")
    
    config = {
        'DATA_SOURCES': {
            'arxiv': {
                'base_url': 'http://export.arxiv.org/api/query',
                'categories': ['q-bio', 'cs.AI', 'cs.LG', 'stat.ML']
            }
        },
        'CRAWL_DELAY': 1,
        'MAX_PAPERS_PER_QUERY': 5
    }
    
    crawler = ArxivCrawler(config)
    
    try:
        # 测试搜索
        papers = crawler.search_papers("machine learning", max_results=3)
        print(f"arXiv搜索结果: {len(papers)} 篇论文")
        
        if papers:
            print("第一篇论文:")
            paper = papers[0]
            print(f"  标题: {paper.get('title', 'N/A')[:100]}...")
            print(f"  作者: {', '.join(paper.get('authors', [])[:3])}")
            print(f"  分类: {paper.get('journal', 'N/A')}")
            print(f"  发表日期: {paper.get('publication_date', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"arXiv爬虫测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("MedLitAgent 爬虫功能测试")
    print("=" * 50)
    
    # 测试PubMed爬虫
    pubmed_success = test_pubmed_crawler()
    
    # 测试arXiv爬虫
    arxiv_success = test_arxiv_crawler()
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"PubMed爬虫: {'✓ 成功' if pubmed_success else '✗ 失败'}")
    print(f"arXiv爬虫: {'✓ 成功' if arxiv_success else '✗ 失败'}")
    
    if pubmed_success and arxiv_success:
        print("\n🎉 所有爬虫测试通过！")
        print("您现在可以使用以下命令开始爬取文献:")
        print("  python main.py crawl 'machine learning' --sources pubmed arxiv --max-results 50")
    else:
        print("\n⚠️  部分爬虫测试失败，请检查网络连接和配置。")

if __name__ == '__main__':
    main()