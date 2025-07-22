#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Official Accounts (公众号) Crawler Configuration
====================================================

Specialized configuration for WeChat Official Accounts crawler.
"""

import os
from typing import Dict, List, Optional

# WeChat Official Accounts Crawler Settings
GONGZHONGHAO_CONFIG = {
    # Browser settings optimized for WeChat
    'headless': True,
    'window_size': '1920,1080',
    'timeout': 30,
    
    # Anti-detection settings for WeChat
    'random_delay_min': 2,  # Longer delays for WeChat
    'random_delay_max': 5,
    'retry_attempts': 3,
    'retry_delay': 3,
    
    # WeChat-specific rate limiting
    'max_concurrent_requests': 3,  # Lower for WeChat
    'max_posts_per_account': 20,
    'max_accounts_per_search': 10,
    'max_articles_per_search': 50,
    
    # Content extraction settings
    'extract_full_content': True,
    'extract_images': True,
    'extract_comments': False,  # Usually not available
    'extract_read_count': True,
    'extract_like_count': True,
    
    # Output settings
    'output_format': 'both',  # 'csv', 'json', or 'both'
    'timestamp_format': '%Y%m%d_%H%M%S',
    'filename_prefix': 'wechat_gongzhonghao',
}

# WeChat Official Account Categories
ACCOUNT_CATEGORIES = {
    'technology': {
        'keywords': ['人工智能', '科技', '技术', '互联网', '编程', '开发', '软件', '硬件'],
        'description': '科技类公众号'
    },
    'business': {
        'keywords': ['商业', '创业', '投资', '金融', '经济', '管理', '营销', '企业'],
        'description': '商业财经类公众号'
    },
    'education': {
        'keywords': ['教育', '学习', '培训', '考试', '技能', '知识', '课程', '学校'],
        'description': '教育培训类公众号'
    },
    'health': {
        'keywords': ['健康', '医疗', '养生', '运动', '营养', '心理', '疾病', '保健'],
        'description': '健康医疗类公众号'
    },
    'lifestyle': {
        'keywords': ['生活', '旅行', '美食', '时尚', '娱乐', '文化', '艺术', '摄影'],
        'description': '生活方式类公众号'
    },
    'news': {
        'keywords': ['新闻', '时事', '政治', '社会', '国际', '军事', '历史', '观点'],
        'description': '新闻资讯类公众号'
    },
    'finance': {
        'keywords': ['理财', '股票', '基金', '保险', '银行', '债券', '外汇', '投资'],
        'description': '金融理财类公众号'
    }
}

# Hot Topics to Monitor (regularly updated)
HOT_TOPICS = [
    # Technology
    'ChatGPT', 'OpenAI', 'GPT-4', '人工智能', '机器学习', '深度学习',
    '自动驾驶', '区块链', '元宇宙', '量子计算', '5G', '云计算',
    
    # Business & Economics
    '新能源', '电动车', '特斯拉', '比亚迪', '芯片', '半导体',
    '房地产', '股市', '经济', '通胀', '央行', '利率',
    
    # Social & Culture
    '疫情', '防控', '疫苗', '教育改革', '双减政策', '就业',
    '生育政策', '养老', '医保', '社保', '房价', '租房',
    
    # International
    '中美关系', '俄乌冲突', '台海', '朝鲜', '日本', '韩国',
    '欧盟', '英国', '印度', '一带一路', 'RCEP', '东盟'
]

# WeChat Specific CSS Selectors
WECHAT_SELECTORS = {
    # Account search results
    'account_search': {
        'result_container': '.results',
        'account_name': 'h3',
        'wechat_id': 'label:contains("微信号")',
        'description': 'dl dd',
        'profile_link': 'a',
        'qr_code': 'img[src*="qr"]',
        'verification': '.sp-tit'
    },
    
    # Article search results
    'article_search': {
        'result_container': '.news-box',
        'title': 'h3 a, h4 a',
        'account_name': 'a[uigs="account_name"]',
        'publish_date': '.s2',
        'summary': '.txt-info',
        'thumbnail': 'img',
        'read_count': 'span:contains("阅读")'
    },
    
    # Account profile page
    'profile_page': {
        'post_container': '.weui_media_box, .msg_card, .appmsg_item',
        'post_title': '.weui_media_title, .news_lst_title, h4, .appmsg_title',
        'post_link': 'a',
        'post_date': '.weui_media_extra_info, .news_lst_time, .publish_time',
        'post_summary': '.weui_media_desc, .news_lst_desc, .digest',
        'post_thumbnail': 'img'
    },
    
    # Article content page
    'article_content': {
        'title': 'h1.rich_media_title, #activity-name',
        'author': '#js_name, .rich_media_meta_text',
        'publish_time': '#publish_time, .rich_media_meta_text',
        'content': '#js_content',
        'read_count': '#readNum3, .read_num, [id*="read"]',
        'like_count': '#likeNum3, .like_num, [id*="like"]',
        'images': '#js_content img',
        'tags': '.tag, .category, [class*="tag"]'
    }
}

# Search Strategies
SEARCH_STRATEGIES = {
    'broad_search': {
        'description': '广泛搜索策略',
        'max_pages': 3,
        'delay_between_pages': 5,
        'include_verified_only': False
    },
    'focused_search': {
        'description': '精确搜索策略', 
        'max_pages': 1,
        'delay_between_pages': 3,
        'include_verified_only': True
    },
    'deep_search': {
        'description': '深度搜索策略',
        'max_pages': 5,
        'delay_between_pages': 8,
        'include_verified_only': False,
        'extract_full_content': True
    }
}

# Content Filters for WeChat Official Accounts
CONTENT_FILTERS = {
    'min_title_length': 3,
    'max_title_length': 200,
    'min_content_length': 100,
    'exclude_keywords': [
        '广告', '推广', '删除', '测试', '招聘', '求职',
        '微商', '代理', '加盟', '刷单', '兼职'
    ],
    'verified_accounts_only': False,
    'min_read_count': 0,
    'recent_days_only': 365  # Only articles from last 365 days
}

# Account Quality Indicators
ACCOUNT_QUALITY_METRICS = {
    'has_verification': 2,  # Weight for verified accounts
    'has_description': 1,   # Weight for accounts with description
    'has_wechat_id': 1,     # Weight for accounts with WeChat ID
    'has_qr_code': 1,       # Weight for accounts with QR code
    'description_length_bonus': 0.1  # Bonus per 10 chars in description
}

# Rate Limiting Settings (Aggressive for WeChat)
RATE_LIMITING = {
    'requests_per_minute': 20,  # Conservative rate
    'requests_per_hour': 500,   # Daily limit consideration
    'cool_down_period': 600,    # 10 minutes cool down if rate limited
    'exponential_backoff': True,
    'max_backoff_time': 300     # 5 minutes max backoff
}

# Data Storage Settings
STORAGE_SETTINGS = {
    'data_dir': 'gongzhonghao_data',
    'accounts_subdir': 'accounts',
    'articles_subdir': 'articles', 
    'images_subdir': 'images',
    'logs_subdir': 'logs',
    'backup_subdir': 'backups',
    'auto_backup': True,
    'compress_old_files': True,
    'days_before_compression': 7
}

# Chrome Options Optimized for WeChat
CHROME_OPTIONS_WECHAT = {
    'basic': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--disable-plugins'
    ],
    'stealth': [
        '--no-sandbox',
        '--disable-dev-shm-usage', 
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=VizDisplayCompositor',
        '--disable-ipc-flooding-protection'
    ],
    'mobile_simulation': [
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
        '--window-size=375,812'
    ]
}

# User Agent Pool (WeChat Mobile/Desktop)
USER_AGENTS_WECHAT = [
    # WeChat Mobile
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f2f) NetType/WIFI Language/zh_CN',
    'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36 MicroMessenger/8.0.15',
    
    # Regular Mobile
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
    
    # Desktop
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
]

# Monitoring and Analytics
MONITORING_CONFIG = {
    'enable_analytics': True,
    'track_success_rate': True,
    'track_response_times': True,
    'alert_on_errors': True,
    'daily_summary': True,
    'trending_analysis': True
}

# API Endpoints (if available)
API_ENDPOINTS_WECHAT = {
    'sogou_search': 'https://weixin.sogou.com/weixin',
    'wechat_search': 'https://mp.weixin.qq.com/cgi-bin/searchbiz',
    'article_stats': 'https://mp.weixin.qq.com/misc/appmsgstat',
    'profile_info': 'https://mp.weixin.qq.com/profile'
}

# Environment Variables Support
def load_gongzhonghao_env_config():
    """Load WeChat Official Accounts specific environment variables"""
    env_config = {}
    
    # Load specific settings from environment
    if os.getenv('WECHAT_GZH_HEADLESS'):
        env_config['headless'] = os.getenv('WECHAT_GZH_HEADLESS').lower() == 'true'
    
    if os.getenv('WECHAT_GZH_PROXY'):
        env_config['proxy'] = os.getenv('WECHAT_GZH_PROXY')
    
    if os.getenv('WECHAT_GZH_DATA_DIR'):
        env_config['data_dir'] = os.getenv('WECHAT_GZH_DATA_DIR')
        
    if os.getenv('WECHAT_GZH_MAX_POSTS'):
        env_config['max_posts_per_account'] = int(os.getenv('WECHAT_GZH_MAX_POSTS'))
    
    return env_config

# Validation Functions
def validate_gongzhonghao_config():
    """Validate WeChat Official Accounts configuration"""
    errors = []
    
    # Check rate limits
    if RATE_LIMITING['requests_per_minute'] > 30:
        errors.append("requests_per_minute should not exceed 30 for WeChat")
    
    # Check concurrent requests
    if GONGZHONGHAO_CONFIG['max_concurrent_requests'] > 5:
        errors.append("max_concurrent_requests should not exceed 5 for WeChat")
    
    # Check delays
    if GONGZHONGHAO_CONFIG['random_delay_min'] < 2:
        errors.append("random_delay_min should be at least 2 seconds for WeChat")
    
    if errors:
        print("WeChat Official Accounts Configuration warnings:")
        for error in errors:
            print(f"  - {error}")

# Setup Functions
def setup_gongzhonghao_directories():
    """Setup directories for WeChat Official Accounts crawler"""
    base_dir = STORAGE_SETTINGS['data_dir']
    subdirs = [
        STORAGE_SETTINGS['accounts_subdir'],
        STORAGE_SETTINGS['articles_subdir'],
        STORAGE_SETTINGS['images_subdir'],
        STORAGE_SETTINGS['logs_subdir'],
        STORAGE_SETTINGS['backup_subdir']
    ]
    
    os.makedirs(base_dir, exist_ok=True)
    for subdir in subdirs:
        full_path = os.path.join(base_dir, subdir)
        os.makedirs(full_path, exist_ok=True)

if __name__ == "__main__":
    # Validate and setup when run directly
    print("WeChat Official Accounts Crawler Configuration")
    print("=" * 50)
    
    validate_gongzhonghao_config()
    setup_gongzhonghao_directories()
    
    print("Configuration validated and directories created.")
    print(f"Data directory: {STORAGE_SETTINGS['data_dir']}")
    print(f"Supported categories: {list(ACCOUNT_CATEGORIES.keys())}")
    print(f"Hot topics count: {len(HOT_TOPICS)}")
    print(f"User agents count: {len(USER_AGENTS_WECHAT)}")