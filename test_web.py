#!/usr/bin/env python3
"""
简单的Web服务测试脚本
"""

import requests
import time
import sys
import subprocess
import signal
import os

def test_web_service():
    """测试Web服务"""
    print("🧪 测试MedLitAgent Web服务")
    print("=" * 50)
    
    # 启动Web服务
    print("1. 启动Web服务...")
    process = subprocess.Popen([
        sys.executable, "main.py", "web", 
        "--host", "0.0.0.0", 
        "--port", "12000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待服务启动
    print("2. 等待服务启动...")
    for i in range(20):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:12000/api/health", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ 服务在 {i+1} 秒后启动成功")
                break
        except:
            pass
        if i == 19:
            print("   ⚠️  服务启动超时，继续测试...")
        else:
            print(f"   等待中... ({i+1}/20)")
    
    try:
        # 测试健康检查端点
        print("3. 测试健康检查端点...")
        response = requests.get("http://localhost:12000/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
        
        # 测试统计信息端点
        print("4. 测试统计信息端点...")
        response = requests.get("http://localhost:12000/api/statistics", timeout=5)
        if response.status_code == 200:
            print("   ✅ 统计信息获取成功")
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {}).get('database', {})
                print(f"   论文数: {stats.get('total_papers', 0)}")
                print(f"   关键词数: {stats.get('total_keywords', 0)}")
            else:
                print(f"   ⚠️  统计信息返回错误: {data.get('error')}")
        else:
            print(f"   ❌ 统计信息获取失败: {response.status_code}")
        
        # 测试分类端点
        print("5. 测试分类端点...")
        response = requests.get("http://localhost:12000/api/categories", timeout=5)
        if response.status_code == 200:
            print("   ✅ 分类信息获取成功")
            data = response.json()
            if data.get('success'):
                categories = data.get('data', [])
                print(f"   分类数量: {len(categories)}")
                if categories:
                    print(f"   示例分类: {categories[0].get('display_name', 'N/A')}")
            else:
                print(f"   ⚠️  分类信息返回错误: {data.get('error')}")
        else:
            print(f"   ❌ 分类信息获取失败: {response.status_code}")
        
        # 测试主页
        print("6. 测试主页...")
        response = requests.get("http://localhost:12000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ 主页访问成功")
            if "MedLitAgent" in response.text:
                print("   ✅ 页面内容正确")
            else:
                print("   ⚠️  页面内容可能有问题")
        else:
            print(f"   ❌ 主页访问失败: {response.status_code}")
        
        # 测试仪表板页面
        print("7. 测试仪表板页面...")
        response = requests.get("http://localhost:12000/dashboard", timeout=5)
        if response.status_code == 200:
            print("   ✅ 仪表板页面访问成功")
        else:
            print(f"   ❌ 仪表板页面访问失败: {response.status_code}")
        
        # 测试搜索页面
        print("8. 测试搜索页面...")
        response = requests.get("http://localhost:12000/search", timeout=5)
        if response.status_code == 200:
            print("   ✅ 搜索页面访问成功")
        else:
            print(f"   ❌ 搜索页面访问失败: {response.status_code}")
        
        print("\n🎉 Web服务测试完成!")
        print(f"🌐 访问地址: http://localhost:12000")
        print(f"📊 仪表板: http://localhost:12000/dashboard")
        print(f"🔍 搜索页面: http://localhost:12000/search")
        print(f"🕷️  爬取页面: http://localhost:12000/crawl")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        # 停止Web服务
        print("\n9. 停止Web服务...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("   ✅ Web服务已停止")

if __name__ == "__main__":
    success = test_web_service()
    sys.exit(0 if success else 1)