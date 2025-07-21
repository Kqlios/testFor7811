#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for WeChat Crawler
=====================================

This script tests basic functionality without requiring all dependencies.
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Test if all modules can be imported"""
    print("Testing module imports...")
    
    try:
        # Test basic Python modules
        import json
        import time
        import random
        import hashlib
        from datetime import datetime, timedelta
        from typing import List, Dict, Optional
        print("✓ Basic Python modules imported successfully")
        
        # Test if our modules can be imported (syntax check)
        import ast
        
        # Check if our main files have valid syntax
        files_to_check = [
            'wechat_crawler.py',
            'config.py',
            'utils.py',
            'example_usage.py'
        ]
        
        for filename in files_to_check:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                try:
                    ast.parse(content)
                    print(f"✓ {filename} has valid Python syntax")
                except SyntaxError as e:
                    print(f"✗ {filename} has syntax error: {e}")
                    return False
            else:
                print(f"⚠ {filename} not found")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_utils():
    """Test utility functions that don't require external dependencies"""
    print("\nTesting utility functions...")
    
    try:
        # Simple utility tests
        from utils import (
            clean_text,
            extract_post_id,
            generate_filename,
            create_url_hash,
            is_valid_wechat_url,
            parse_wechat_date
        )
        
        # Test text cleaning
        cleaned = clean_text("  Hello   World!  \n\n  ")
        assert cleaned == "Hello World", f"Expected 'Hello World', got '{cleaned}'"
        print("✓ clean_text function works")
        
        # Test URL validation
        valid_url = "https://mp.weixin.qq.com/s/abc123"
        invalid_url = "https://example.com/test"
        assert is_valid_wechat_url(valid_url) == True
        assert is_valid_wechat_url(invalid_url) == False
        print("✓ is_valid_wechat_url function works")
        
        # Test filename generation
        filename = generate_filename("test", "csv", include_timestamp=False)
        assert filename == "test.csv"
        print("✓ generate_filename function works")
        
        # Test URL hash
        url_hash = create_url_hash("https://example.com")
        assert len(url_hash) == 32  # MD5 hash length
        print("✓ create_url_hash function works")
        
        # Test post ID extraction
        post_id = extract_post_id("https://mp.weixin.qq.com/s/abc123def")
        assert post_id == "abc123def"
        print("✓ extract_post_id function works")
        
        return True
        
    except Exception as e:
        print(f"✗ Utility test error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import (
            CRAWLER_CONFIG,
            API_ENDPOINTS,
            SEARCH_KEYWORDS,
            validate_config,
            setup_directories
        )
        
        # Test config structure
        assert isinstance(CRAWLER_CONFIG, dict)
        assert 'headless' in CRAWLER_CONFIG
        assert 'timeout' in CRAWLER_CONFIG
        print("✓ CRAWLER_CONFIG structure is valid")
        
        # Test API endpoints
        assert isinstance(API_ENDPOINTS, dict)
        assert 'sogou_search' in API_ENDPOINTS
        print("✓ API_ENDPOINTS structure is valid")
        
        # Test search keywords
        assert isinstance(SEARCH_KEYWORDS, dict)
        assert 'technology' in SEARCH_KEYWORDS
        assert isinstance(SEARCH_KEYWORDS['technology'], list)
        print("✓ SEARCH_KEYWORDS structure is valid")
        
        # Test validation
        validate_config()
        print("✓ Configuration validation completed")
        
        # Test directory setup
        setup_directories()
        print("✓ Directory setup completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test error: {e}")
        return False

def test_file_structure():
    """Test if all necessary files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'wechat_crawler.py',
        'config.py',
        'utils.py',
        'example_usage.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} exists ({size} bytes)")
        else:
            print(f"✗ {filename} missing")
            all_exist = False
    
    return all_exist

def create_sample_data():
    """Create sample data files for testing"""
    print("\nCreating sample data...")
    
    try:
        sample_posts = [
            {
                'title': '人工智能发展趋势分析',
                'link': 'https://mp.weixin.qq.com/s/sample123',
                'author': '科技前沿',
                'publish_date': '2024-01-15',
                'description': '深度解析人工智能的最新发展趋势...',
                'content': '人工智能作为21世纪最重要的技术革命之一...',
                'read_count': '1200',
                'like_count': '89',
                'images': ['https://example.com/image1.jpg'],
                'crawled_at': datetime.now().isoformat()
            },
            {
                'title': '机器学习算法优化技巧',
                'link': 'https://mp.weixin.qq.com/s/sample456',
                'author': 'AI研究院',
                'publish_date': '2024-01-14',
                'description': '分享机器学习算法的优化方法...',
                'content': '在机器学习项目中，算法优化是提升性能的关键...',
                'read_count': '856',
                'like_count': '67',
                'images': [],
                'crawled_at': datetime.now().isoformat()
            }
        ]
        
        # Save sample data as JSON
        import json
        with open('sample_posts.json', 'w', encoding='utf-8') as f:
            json.dump(sample_posts, f, ensure_ascii=False, indent=2)
        
        print("✓ Sample JSON data created")
        
        # Save sample data as CSV (simple version)
        csv_content = "title,link,author,publish_date,read_count,like_count\n"
        for post in sample_posts:
            csv_content += f'"{post["title"]}","{post["link"]}","{post["author"]}","{post["publish_date"]}","{post["read_count"]}","{post["like_count"]}"\n'
        
        with open('sample_posts.csv', 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print("✓ Sample CSV data created")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def main():
    """Run all tests"""
    print("WeChat Crawler Test Suite")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Utility Functions", test_utils),
        ("Sample Data Creation", create_sample_data),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The WeChat crawler is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run example: python example_usage.py")
        print("3. Check the README.md for detailed usage instructions")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)