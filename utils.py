#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Crawler Utilities
========================

Utility functions for the WeChat crawler.
"""

import os
import re
import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from urllib.parse import urlparse, parse_qs
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    
from pathlib import Path
import zipfile
import logging

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep Chinese characters
    text = re.sub(r'[^\w\s\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


def extract_post_id(url: str) -> Optional[str]:
    """
    Extract post ID from WeChat article URL
    
    Args:
        url (str): WeChat article URL
        
    Returns:
        str: Post ID if found, None otherwise
    """
    try:
        # Pattern for WeChat article URLs
        pattern = r'https://mp\.weixin\.qq\.com/s/([A-Za-z0-9_-]+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        # Alternative pattern with parameters
        pattern = r'https://mp\.weixin\.qq\.com/s\?.*__biz=([^&]+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract post ID from URL {url}: {e}")
        return None


def generate_filename(prefix: str = "wechat", 
                     extension: str = "csv", 
                     include_timestamp: bool = True) -> str:
    """
    Generate a filename with optional timestamp
    
    Args:
        prefix (str): Filename prefix
        extension (str): File extension
        include_timestamp (bool): Whether to include timestamp
        
    Returns:
        str: Generated filename
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    else:
        return f"{prefix}.{extension}"


def create_url_hash(url: str) -> str:
    """
    Create a hash for a URL to use as unique identifier
    
    Args:
        url (str): URL to hash
        
    Returns:
        str: MD5 hash of the URL
    """
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def is_valid_wechat_url(url: str) -> bool:
    """
    Check if a URL is a valid WeChat article URL
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid WeChat URL
    """
    if not url:
        return False
    
    # Check if it's a WeChat article URL
    wechat_patterns = [
        r'https://mp\.weixin\.qq\.com/s/',
        r'https://mp\.weixin\.qq\.com/s\?',
    ]
    
    for pattern in wechat_patterns:
        if re.match(pattern, url):
            return True
    
    return False


def parse_wechat_date(date_str: str) -> Optional[datetime]:
    """
    Parse WeChat date strings to datetime objects
    
    Args:
        date_str (str): Date string from WeChat
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not date_str:
        return None
    
    # Common WeChat date formats
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # 2024-01-01
        r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2024年1月1日
        r'(\d{1,2}月\d{1,2}日)',  # 1月1日
        r'昨天',
        r'今天',
        r'前天',
    ]
    
    try:
        # Try to parse exact date formats
        for pattern in date_patterns[:3]:
            match = re.search(pattern, date_str)
            if match:
                date_part = match.group(1)
                if '年' in date_part:
                    # Chinese format: 2024年1月1日
                    date_part = re.sub(r'年|月', '-', date_part).replace('日', '')
                    return datetime.strptime(date_part, '%Y-%m-%d')
                elif '-' in date_part:
                    # Standard format: 2024-01-01
                    return datetime.strptime(date_part, '%Y-%m-%d')
                else:
                    # Month-day only: 1月1日
                    current_year = datetime.now().year
                    date_part = re.sub(r'月', '-', date_part).replace('日', '')
                    return datetime.strptime(f"{current_year}-{date_part}", '%Y-%m-%d')
        
        # Handle relative dates
        if '今天' in date_str:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif '昨天' in date_str:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        elif '前天' in date_str:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to parse date string '{date_str}': {e}")
        return None


def filter_duplicate_posts(posts: List[Dict], key: str = 'link') -> List[Dict]:
    """
    Remove duplicate posts based on a key
    
    Args:
        posts (List[Dict]): List of post dictionaries
        key (str): Key to use for deduplication
        
    Returns:
        List[Dict]: Deduplicated list of posts
    """
    seen = set()
    unique_posts = []
    
    for post in posts:
        if key in post and post[key] not in seen:
            seen.add(post[key])
            unique_posts.append(post)
    
    logger.info(f"Filtered {len(posts) - len(unique_posts)} duplicate posts")
    return unique_posts


def validate_post_data(post: Dict) -> bool:
    """
    Validate if post data contains required fields
    
    Args:
        post (Dict): Post data dictionary
        
    Returns:
        bool: True if valid
    """
    required_fields = ['title', 'link']
    
    for field in required_fields:
        if field not in post or not post[field]:
            return False
    
    # Check if title is reasonable length
    if len(post['title']) < 3 or len(post['title']) > 200:
        return False
    
    # Check if link is valid WeChat URL
    if not is_valid_wechat_url(post['link']):
        return False
    
    return True


def merge_post_data(basic_data: Dict, detailed_data: Dict) -> Dict:
    """
    Merge basic post data with detailed content data
    
    Args:
        basic_data (Dict): Basic post information
        detailed_data (Dict): Detailed post content
        
    Returns:
        Dict: Merged post data
    """
    merged = basic_data.copy()
    
    # Update with detailed data, but don't overwrite existing values with empty ones
    for key, value in detailed_data.items():
        if value or key not in merged:
            merged[key] = value
    
    return merged


def save_data_with_backup(data: List[Dict], filename: str, backup_dir: str = "backups") -> bool:
    """
    Save data with automatic backup of existing files
    
    Args:
        data (List[Dict]): Data to save
        filename (str): Target filename
        backup_dir (str): Backup directory
        
    Returns:
        bool: True if successful
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # If file exists, create backup
        if os.path.exists(filename):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = os.path.join(backup_dir, f"{os.path.basename(filename)}.{timestamp}.bak")
            os.rename(filename, backup_filename)
            logger.info(f"Created backup: {backup_filename}")
        
        # Save new data
        if filename.endswith('.csv'):
            if HAS_PANDAS:
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            else:
                # Fallback CSV writing without pandas
                if data:
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
        elif filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        logger.info(f"Data saved to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        return False


def compress_old_files(directory: str, days_old: int = 7) -> None:
    """
    Compress files older than specified days
    
    Args:
        directory (str): Directory to check
        days_old (int): Files older than this many days will be compressed
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.zip'):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_time < cutoff_date:
                    # Compress the file
                    zip_path = file_path.with_suffix(file_path.suffix + '.zip')
                    
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(file_path, file_path.name)
                    
                    # Remove original file
                    file_path.unlink()
                    logger.info(f"Compressed old file: {file_path} -> {zip_path}")
                    
    except Exception as e:
        logger.error(f"Failed to compress old files: {e}")


def calculate_crawling_stats(posts: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics for crawled posts
    
    Args:
        posts (List[Dict]): List of crawled posts
        
    Returns:
        Dict: Statistics dictionary
    """
    if not posts:
        return {}
    
    stats = {
        'total_posts': len(posts),
        'unique_authors': len(set(post.get('author', '') for post in posts if post.get('author'))),
        'date_range': {},
        'avg_title_length': 0,
        'avg_content_length': 0,
        'posts_with_images': 0,
    }
    
    # Calculate date range
    dates = []
    for post in posts:
        if 'publish_date' in post:
            parsed_date = parse_wechat_date(post['publish_date'])
            if parsed_date:
                dates.append(parsed_date)
    
    if dates:
        stats['date_range'] = {
            'earliest': min(dates).isoformat(),
            'latest': max(dates).isoformat(),
            'span_days': (max(dates) - min(dates)).days
        }
    
    # Calculate average lengths
    titles = [post.get('title', '') for post in posts if post.get('title')]
    if titles:
        stats['avg_title_length'] = sum(len(title) for title in titles) / len(titles)
    
    contents = [post.get('content', '') for post in posts if post.get('content')]
    if contents:
        stats['avg_content_length'] = sum(len(content) for content in contents) / len(contents)
    
    # Count posts with images
    stats['posts_with_images'] = sum(1 for post in posts if post.get('images') and len(post['images']) > 0)
    
    return stats


def random_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """
    Add a random delay to avoid detection
    
    Args:
        min_delay (float): Minimum delay in seconds
        max_delay (float): Maximum delay in seconds
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def rate_limit_check(last_request_time: Optional[float], 
                    min_interval: float = 1.0) -> bool:
    """
    Check if enough time has passed since last request
    
    Args:
        last_request_time (float): Timestamp of last request
        min_interval (float): Minimum interval between requests
        
    Returns:
        bool: True if OK to proceed
    """
    if last_request_time is None:
        return True
    
    elapsed = time.time() - last_request_time
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a file
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        Dict: File information
    """
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'exists': True
        }
    except FileNotFoundError:
        return {'exists': False}
    except Exception as e:
        return {'exists': False, 'error': str(e)}


def create_summary_report(posts: List[Dict], output_file: str = None) -> str:
    """
    Create a summary report of crawled posts
    
    Args:
        posts (List[Dict]): List of crawled posts
        output_file (str): Optional output file path
        
    Returns:
        str: Summary report text
    """
    stats = calculate_crawling_stats(posts)
    
    report = f"""
WeChat Crawler Summary Report
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Basic Statistics:
- Total posts crawled: {stats.get('total_posts', 0)}
- Unique authors: {stats.get('unique_authors', 0)}
- Posts with images: {stats.get('posts_with_images', 0)}

Content Analysis:
- Average title length: {stats.get('avg_title_length', 0):.1f} characters
- Average content length: {stats.get('avg_content_length', 0):.1f} characters

Date Range:
- Earliest post: {stats.get('date_range', {}).get('earliest', 'N/A')}
- Latest post: {stats.get('date_range', {}).get('latest', 'N/A')}
- Time span: {stats.get('date_range', {}).get('span_days', 0)} days

Top Authors by Post Count:
"""
    
    # Add top authors
    if posts:
        author_counts = {}
        for post in posts:
            author = post.get('author', 'Unknown')
            author_counts[author] = author_counts.get(author, 0) + 1
        
        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (author, count) in enumerate(sorted_authors[:10], 1):
            report += f"{i:2d}. {author}: {count} posts\n"
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Summary report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save summary report: {e}")
    
    return report


if __name__ == "__main__":
    # Test utility functions
    print("Testing WeChat Crawler Utilities")
    
    # Test URL validation
    test_urls = [
        "https://mp.weixin.qq.com/s/abc123",
        "https://mp.weixin.qq.com/s?__biz=abc&mid=123",
        "https://example.com/invalid",
        ""
    ]
    
    for url in test_urls:
        print(f"URL: {url} - Valid: {is_valid_wechat_url(url)}")
    
    # Test date parsing
    test_dates = ["2024-01-01", "2024年1月1日", "今天", "昨天", "1月15日"]
    for date_str in test_dates:
        parsed = parse_wechat_date(date_str)
        print(f"Date: {date_str} - Parsed: {parsed}")
    
    print("Utility tests completed!")