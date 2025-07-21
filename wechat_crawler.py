#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Posts Crawler
===================

A comprehensive web crawler for WeChat public account posts.
Supports multiple crawling methods with anti-detection measures.

Author: AI Assistant
Date: 2024
"""

import requests
import time
import json
import re
import os
import random
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime, timedelta
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from fake_useragent import UserAgent
    HAS_FAKE_USERAGENT = True
except ImportError:
    HAS_FAKE_USERAGENT = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import asyncio
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from retrying import retry
    HAS_RETRYING = True
except ImportError:
    HAS_RETRYING = False
    # Simple retry decorator fallback
    def retry(stop_max_attempt_number=3, wait_fixed=2000):
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(stop_max_attempt_number):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == stop_max_attempt_number - 1:
                            raise e
                        time.sleep(wait_fixed / 1000.0)
                return None
            return wrapper
        return decorator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeChatCrawler:
    """
    WeChat Posts Crawler with multiple crawling strategies
    """
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        """
        Initialize the WeChat crawler
        
        Args:
            headless (bool): Whether to run browser in headless mode
            proxy (str, optional): Proxy server URL
        """
        if HAS_FAKE_USERAGENT:
            self.ua = UserAgent()
        else:
            # Fallback user agent
            class FallbackUA:
                @property
                def random(self):
                    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            self.ua = FallbackUA()
        
        self.session = requests.Session()
        self.proxy = proxy
        self.headless = headless
        self.driver = None
        self.posts_data = []
        
        # Common headers
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
            
        # WeChat API endpoints (may need updates)
        self.api_endpoints = {
            'search': 'https://weixin.sogou.com/weixin',
            'article': 'https://mp.weixin.qq.com/s/',
            'profile': 'https://mp.weixin.qq.com/profile'
        }
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """
        Setup Selenium Chrome driver with anti-detection measures
        """
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Anti-detection options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def search_wechat_accounts(self, keyword: str, page: int = 1) -> List[Dict]:
        """
        Search for WeChat public accounts using Sogou search
        
        Args:
            keyword (str): Search keyword
            page (int): Page number
            
        Returns:
            List[Dict]: List of account information
        """
        logger.info(f"Searching for WeChat accounts with keyword: {keyword}")
        
        try:
            params = {
                'type': 1,  # 1 for accounts, 2 for articles
                'query': keyword,
                'ie': 'utf8',
                'page': page
            }
            
            response = self.session.get(
                self.api_endpoints['search'],
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            if not HAS_BS4:
                logger.error("BeautifulSoup4 is required for HTML parsing")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            accounts = []
            
            # Parse search results
            result_items = soup.find_all('div', class_='results')
            for item in result_items:
                try:
                    account_info = self._parse_account_info(item)
                    if account_info:
                        accounts.append(account_info)
                except Exception as e:
                    logger.warning(f"Failed to parse account info: {e}")
                    continue
            
            logger.info(f"Found {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to search WeChat accounts: {e}")
            return []
    
    def _parse_account_info(self, item) -> Optional[Dict]:
        """
        Parse account information from search result item
        """
        try:
            # Extract account name
            name_elem = item.find('h3')
            if not name_elem:
                return None
            account_name = name_elem.get_text(strip=True)
            
            # Extract account ID (WeChat ID)
            wechat_id = ""
            id_elem = item.find('span', class_='sp-wx')
            if id_elem:
                wechat_id = id_elem.get_text(strip=True).replace('微信号：', '')
            
            # Extract description
            desc_elem = item.find('span', class_='sp-desc')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract profile link
            link_elem = item.find('a')
            profile_link = link_elem.get('href') if link_elem else ""
            
            return {
                'account_name': account_name,
                'wechat_id': wechat_id,
                'description': description,
                'profile_link': profile_link,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing account info: {e}")
            return None
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_account_posts(self, account_url: str, max_posts: int = 10) -> List[Dict]:
        """
        Get posts from a WeChat account using Selenium
        
        Args:
            account_url (str): WeChat account profile URL
            max_posts (int): Maximum number of posts to crawl
            
        Returns:
            List[Dict]: List of post information
        """
        logger.info(f"Getting posts from account: {account_url}")
        
        if not self.driver:
            self.driver = self.setup_selenium_driver()
        
        try:
            self.driver.get(account_url)
            self._random_delay(2, 5)
            
            posts = []
            
            # Wait for posts to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "weui_msg_card"))
            )
            
            # Scroll and collect posts
            post_elements = self.driver.find_elements(By.CLASS_NAME, "weui_msg_card")
            
            for i, post_elem in enumerate(post_elements[:max_posts]):
                try:
                    post_info = self._parse_post_element(post_elem)
                    if post_info:
                        posts.append(post_info)
                        logger.info(f"Crawled post {i+1}: {post_info.get('title', 'No title')[:50]}...")
                    
                    self._random_delay(1, 3)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse post {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully crawled {len(posts)} posts")
            return posts
            
        except TimeoutException:
            logger.error("Timeout waiting for posts to load")
            return []
        except Exception as e:
            logger.error(f"Failed to get account posts: {e}")
            return []
    
    def _parse_post_element(self, post_elem) -> Optional[Dict]:
        """
        Parse post information from a post element
        """
        try:
            # Extract title
            title_elem = post_elem.find_element(By.CSS_SELECTOR, ".weui_media_title, h4")
            title = title_elem.text.strip() if title_elem else "No title"
            
            # Extract link
            link_elem = post_elem.find_element(By.TAG_NAME, "a")
            post_link = link_elem.get_attribute("href") if link_elem else ""
            
            # Extract publish date
            date_elem = post_elem.find_element(By.CSS_SELECTOR, ".weui_media_extra_info, .publish_time")
            publish_date = date_elem.text.strip() if date_elem else ""
            
            # Extract description/summary
            desc_elem = post_elem.find_element(By.CSS_SELECTOR, ".weui_media_desc, .digest")
            description = desc_elem.text.strip() if desc_elem else ""
            
            return {
                'title': title,
                'link': post_link,
                'publish_date': publish_date,
                'description': description,
                'crawled_at': datetime.now().isoformat()
            }
            
        except NoSuchElementException as e:
            logger.warning(f"Element not found when parsing post: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error parsing post element: {e}")
            return None
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_post_content(self, post_url: str) -> Optional[Dict]:
        """
        Get full content of a WeChat post
        
        Args:
            post_url (str): WeChat post URL
            
        Returns:
            Dict: Post content information
        """
        logger.info(f"Getting post content: {post_url}")
        
        try:
            if not self.driver:
                self.driver = self.setup_selenium_driver()
            
            self.driver.get(post_url)
            self._random_delay(3, 6)
            
            # Wait for content to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "js_content"))
            )
            
            # Extract post data
            post_data = {
                'url': post_url,
                'title': self._safe_find_text(By.ID, "activity-name") or 
                        self._safe_find_text(By.CSS_SELECTOR, "h2.rich_media_title"),
                'author': self._safe_find_text(By.ID, "js_name") or
                         self._safe_find_text(By.CSS_SELECTOR, ".rich_media_meta_text"),
                'publish_time': self._safe_find_text(By.ID, "publish_time") or
                               self._safe_find_text(By.CSS_SELECTOR, ".rich_media_meta_text"),
                'content': self._safe_find_text(By.ID, "js_content"),
                'read_count': self._extract_read_count(),
                'like_count': self._extract_like_count(),
                'crawled_at': datetime.now().isoformat()
            }
            
            # Extract images
            post_data['images'] = self._extract_images()
            
            logger.info(f"Successfully extracted post content: {post_data['title'][:50]}...")
            return post_data
            
        except TimeoutException:
            logger.error(f"Timeout loading post content: {post_url}")
            return None
        except Exception as e:
            logger.error(f"Failed to get post content: {e}")
            return None
    
    def _safe_find_text(self, by: By, selector: str) -> str:
        """
        Safely find element text
        """
        try:
            element = self.driver.find_element(by, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _extract_read_count(self) -> str:
        """
        Extract read count from post
        """
        try:
            # Multiple selectors for read count
            selectors = [
                "#readNum3",
                ".read_num",
                "[id*='read']",
                ".media_tool_meta"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and any(char.isdigit() for char in text):
                        return text
                except NoSuchElementException:
                    continue
            
            return "0"
            
        except Exception:
            return "0"
    
    def _extract_like_count(self) -> str:
        """
        Extract like count from post
        """
        try:
            selectors = [
                "#likeNum3",
                ".like_num",
                "[id*='like']",
                ".praise_num"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and any(char.isdigit() for char in text):
                        return text
                except NoSuchElementException:
                    continue
            
            return "0"
            
        except Exception:
            return "0"
    
    def _extract_images(self) -> List[str]:
        """
        Extract image URLs from post
        """
        try:
            images = []
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, "#js_content img")
            
            for img in img_elements:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and src.startswith(('http', '//')):
                    images.append(src)
            
            return images
            
        except Exception as e:
            logger.warning(f"Failed to extract images: {e}")
            return []
    
    def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """
        Add random delay to avoid detection
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def save_to_csv(self, data: List[Dict], filename: str = None):
        """
        Save crawled data to CSV file
        """
        if not data:
            logger.warning("No data to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_posts_{timestamp}.csv"
        
        try:
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
            logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save data to CSV: {e}")
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """
        Save crawled data to JSON file
        """
        if not data:
            logger.warning("No data to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_posts_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")
    
    def close(self):
        """
        Clean up resources
        """
        if self.driver:
            self.driver.quit()
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Async version for better performance
class AsyncWeChatCrawler:
    """
    Asynchronous WeChat crawler for better performance
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        if HAS_AIOHTTP:
            self.semaphore = asyncio.Semaphore(max_concurrent)
        if HAS_FAKE_USERAGENT:
            self.ua = UserAgent()
        else:
            # Fallback user agent
            class FallbackUA:
                @property
                def random(self):
                    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            self.ua = FallbackUA()
    
    async def fetch_url(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """
        Fetch URL content asynchronously
        """
        async with self.semaphore:
            try:
                headers = {'User-Agent': self.ua.random}
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return None
    
    async def batch_crawl_posts(self, post_urls: List[str]) -> List[Dict]:
        """
        Crawl multiple posts concurrently
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, url) for url in post_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            posts = []
            for url, content in zip(post_urls, results):
                if isinstance(content, str) and content:
                    # Parse content here
                    post_data = self._parse_html_content(content, url)
                    if post_data:
                        posts.append(post_data)
            
            return posts
    
    def _parse_html_content(self, html: str, url: str) -> Optional[Dict]:
        """
        Parse HTML content to extract post information
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract basic info
            title = soup.find('h2', class_='rich_media_title')
            title = title.get_text(strip=True) if title else "No title"
            
            content = soup.find('div', id='js_content')
            content = content.get_text(strip=True) if content else ""
            
            return {
                'url': url,
                'title': title,
                'content': content[:1000],  # Truncate for storage
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to parse HTML content: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    crawler = WeChatCrawler(headless=True)
    
    try:
        # Search for accounts
        accounts = crawler.search_wechat_accounts("科技", page=1)
        print(f"Found {len(accounts)} accounts")
        
        # Get posts from first account if available
        if accounts:
            posts = crawler.get_account_posts(accounts[0]['profile_link'], max_posts=5)
            print(f"Found {len(posts)} posts")
            
            # Get detailed content for first post
            if posts:
                content = crawler.get_post_content(posts[0]['link'])
                if content:
                    print(f"Got content for: {content['title']}")
            
            # Save data
            crawler.save_to_csv(posts, "wechat_posts.csv")
            crawler.save_to_json(posts, "wechat_posts.json")
    
    finally:
        crawler.close()