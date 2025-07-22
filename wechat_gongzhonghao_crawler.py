#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Official Accounts (公众号) Crawler
========================================

A specialized web crawler for WeChat Official Accounts (公众号) posts.
Focuses on crawling published articles from WeChat public accounts.

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
from urllib.parse import urljoin, urlparse, parse_qs, quote
from datetime import datetime, timedelta
import hashlib

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
        logging.FileHandler('wechat_gongzhonghao.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeChatOfficialAccountsCrawler:
    """
    WeChat Official Accounts (公众号) Crawler
    Specialized for crawling WeChat public account posts
    """
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        """
        Initialize the WeChat Official Accounts crawler
        
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
        
        # Common headers for requests
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://weixin.sogou.com/',
        }
        
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
            
        # WeChat Official Accounts specific endpoints
        self.endpoints = {
            # Sogou WeChat search - primary method
            'sogou_account_search': 'https://weixin.sogou.com/weixin',
            'sogou_article_search': 'https://weixin.sogou.com/weixin',
            
            # WeChat official endpoints
            'wechat_article': 'https://mp.weixin.qq.com/s/',
            'wechat_profile': 'https://mp.weixin.qq.com/profile',
            
            # Alternative search engines
            'wechat_search_api': 'https://mp.weixin.qq.com/cgi-bin/searchbiz',
        }
    
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """
        Setup Selenium Chrome driver optimized for WeChat crawling
        """
        if not HAS_SELENIUM:
            raise ImportError("Selenium is required for browser automation")
            
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Anti-detection options for WeChat
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # WeChat specific optimizations
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            
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
    def search_official_accounts(self, keyword: str, page: int = 1) -> List[Dict]:
        """
        Search for WeChat Official Accounts (公众号) using Sogou
        
        Args:
            keyword (str): Search keyword
            page (int): Page number
            
        Returns:
            List[Dict]: List of official account information
        """
        logger.info(f"Searching for WeChat Official Accounts with keyword: {keyword}")
        
        try:
            params = {
                'type': 1,  # 1 for accounts, 2 for articles
                'query': keyword,
                'ie': 'utf8',
                'page': page,
                's_from': 'input',
                '_sug_': '0',
                '_sug_type_': ''
            }
            
            response = self.session.get(
                self.endpoints['sogou_account_search'],
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
            
            # Parse search results for official accounts
            result_items = soup.find_all('div', class_='results')
            
            for item in result_items:
                try:
                    account_info = self._parse_official_account_info(item)
                    if account_info:
                        accounts.append(account_info)
                except Exception as e:
                    logger.warning(f"Failed to parse account info: {e}")
                    continue
            
            logger.info(f"Found {len(accounts)} official accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to search WeChat Official Accounts: {e}")
            return []
    
    def _parse_official_account_info(self, item) -> Optional[Dict]:
        """
        Parse official account information from search result item
        """
        try:
            # Extract account name
            name_elem = item.find('h3')
            if not name_elem:
                return None
            
            account_name = name_elem.get_text(strip=True)
            
            # Extract WeChat ID (微信号)
            wechat_id = ""
            id_elem = item.find('label', text='微信号')
            if id_elem and id_elem.parent:
                wechat_id = id_elem.parent.get_text(strip=True).replace('微信号：', '')
            
            # Extract description
            desc_elem = item.find('dl')
            description = ""
            if desc_elem:
                dd_elem = desc_elem.find('dd')
                if dd_elem:
                    description = dd_elem.get_text(strip=True)
            
            # Extract profile link
            link_elem = item.find('a')
            profile_link = ""
            if link_elem and link_elem.get('href'):
                profile_link = link_elem.get('href')
                # Convert relative URL to absolute
                if profile_link.startswith('/'):
                    profile_link = 'https://weixin.sogou.com' + profile_link
            
            # Extract QR code if available
            qr_elem = item.find('img', {'src': re.compile(r'.*qr.*')})
            qr_code = qr_elem.get('src') if qr_elem else ""
            
            # Extract authentication status
            auth_elem = item.find('span', class_='sp-tit')
            authentication = auth_elem.get_text(strip=True) if auth_elem else ""
            
            return {
                'account_name': account_name,
                'wechat_id': wechat_id,
                'description': description,
                'profile_link': profile_link,
                'qr_code': qr_code,
                'authentication': authentication,
                'crawled_at': datetime.now().isoformat(),
                'search_keyword': ''  # Will be filled by caller
            }
            
        except Exception as e:
            logger.warning(f"Error parsing official account info: {e}")
            return None
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def search_account_articles(self, keyword: str, account_name: str = "", page: int = 1) -> List[Dict]:
        """
        Search for articles from WeChat Official Accounts
        
        Args:
            keyword (str): Search keyword for articles
            account_name (str): Specific account name to search within
            page (int): Page number
            
        Returns:
            List[Dict]: List of article information
        """
        logger.info(f"Searching for articles with keyword: {keyword}")
        
        try:
            # Build search query
            if account_name:
                query = f"{keyword} site:{account_name}"
            else:
                query = keyword
            
            params = {
                'type': 2,  # 2 for articles
                'query': query,
                'ie': 'utf8',
                'page': page,
                's_from': 'input'
            }
            
            response = self.session.get(
                self.endpoints['sogou_article_search'],
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            if not HAS_BS4:
                logger.error("BeautifulSoup4 is required for HTML parsing")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Parse search results for articles
            result_items = soup.find_all('div', class_='news-box')
            
            for item in result_items:
                try:
                    article_info = self._parse_article_info(item)
                    if article_info:
                        articles.append(article_info)
                except Exception as e:
                    logger.warning(f"Failed to parse article info: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to search articles: {e}")
            return []
    
    def _parse_article_info(self, item) -> Optional[Dict]:
        """
        Parse article information from search result item
        """
        try:
            # Extract title
            title_elem = item.find('h3') or item.find('h4')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            article_url = title_link.get('href', '')
            
            # Extract account name
            account_elem = item.find('a', {'uigs': 'account_name'})
            account_name = account_elem.get_text(strip=True) if account_elem else ""
            
            # Extract publish date
            date_elem = item.find('span', class_='s2')
            publish_date = date_elem.get_text(strip=True) if date_elem else ""
            
            # Extract summary/description
            summary_elem = item.find('p', class_='txt-info')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Extract thumbnail image
            img_elem = item.find('img')
            thumbnail = img_elem.get('src') if img_elem else ""
            
            # Extract read count if available
            read_elem = item.find('span', text=re.compile(r'阅读|read', re.I))
            read_count = ""
            if read_elem:
                read_text = read_elem.get_text(strip=True)
                read_match = re.search(r'(\d+)', read_text)
                read_count = read_match.group(1) if read_match else ""
            
            return {
                'title': title,
                'url': article_url,
                'account_name': account_name,
                'publish_date': publish_date,
                'summary': summary,
                'thumbnail': thumbnail,
                'read_count': read_count,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing article info: {e}")
            return None
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_account_recent_posts(self, profile_url: str, max_posts: int = 10) -> List[Dict]:
        """
        Get recent posts from an official account's profile page
        
        Args:
            profile_url (str): Official account profile URL
            max_posts (int): Maximum number of posts to retrieve
            
        Returns:
            List[Dict]: List of recent posts
        """
        logger.info(f"Getting recent posts from: {profile_url}")
        
        if not HAS_SELENIUM:
            logger.error("Selenium is required for profile page crawling")
            return []
        
        if not self.driver:
            self.driver = self.setup_selenium_driver()
        
        try:
            self.driver.get(profile_url)
            self._random_delay(3, 6)
            
            posts = []
            
            # Wait for posts to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".weui_media_box, .msg_card"))
            )
            
            # Find post elements
            post_selectors = [
                ".weui_media_box",
                ".msg_card", 
                ".appmsg_item",
                ".news_lst_item"
            ]
            
            post_elements = []
            for selector in post_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    post_elements = elements
                    break
            
            for i, post_elem in enumerate(post_elements[:max_posts]):
                try:
                    post_info = self._parse_post_element_selenium(post_elem)
                    if post_info:
                        posts.append(post_info)
                        logger.info(f"Crawled post {i+1}: {post_info.get('title', 'No title')[:50]}...")
                    
                    self._random_delay(1, 2)
                    
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
    
    def _parse_post_element_selenium(self, post_elem) -> Optional[Dict]:
        """
        Parse post information from a Selenium WebElement
        """
        try:
            # Extract title
            title_selectors = [
                ".weui_media_title",
                ".news_lst_title", 
                "h4",
                ".appmsg_title"
            ]
            
            title = ""
            title_elem = None
            for selector in title_selectors:
                try:
                    title_elem = post_elem.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
            
            # Extract link
            link = ""
            try:
                link_elem = post_elem.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href") or ""
            except NoSuchElementException:
                if title_elem:
                    parent = title_elem.find_element(By.XPATH, "..")
                    link_elem = parent.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href") or ""
            
            # Extract publish date
            date_selectors = [
                ".weui_media_extra_info",
                ".news_lst_time",
                ".publish_time",
                "[class*='time']"
            ]
            
            publish_date = ""
            for selector in date_selectors:
                try:
                    date_elem = post_elem.find_element(By.CSS_SELECTOR, selector)
                    publish_date = date_elem.text.strip()
                    if publish_date:
                        break
                except NoSuchElementException:
                    continue
            
            # Extract description/summary
            desc_selectors = [
                ".weui_media_desc",
                ".news_lst_desc",
                ".digest"
            ]
            
            description = ""
            for selector in desc_selectors:
                try:
                    desc_elem = post_elem.find_element(By.CSS_SELECTOR, selector)
                    description = desc_elem.text.strip()
                    if description:
                        break
                except NoSuchElementException:
                    continue
            
            # Extract thumbnail
            thumbnail = ""
            try:
                img_elem = post_elem.find_element(By.TAG_NAME, "img")
                thumbnail = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
            except NoSuchElementException:
                pass
            
            if not title and not link:
                return None
            
            return {
                'title': title or "No title",
                'url': link,
                'publish_date': publish_date,
                'summary': description,
                'thumbnail': thumbnail,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing post element: {e}")
            return None
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_article_content(self, article_url: str) -> Optional[Dict]:
        """
        Get full content of a WeChat article
        
        Args:
            article_url (str): WeChat article URL
            
        Returns:
            Dict: Article content information
        """
        logger.info(f"Getting article content: {article_url}")
        
        if not HAS_SELENIUM:
            logger.error("Selenium is required for article content extraction")
            return None
        
        if not self.driver:
            self.driver = self.setup_selenium_driver()
        
        try:
            self.driver.get(article_url)
            self._random_delay(3, 6)
            
            # Wait for content to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "js_content"))
            )
            
            # Extract article data
            article_data = {
                'url': article_url,
                'title': self._safe_find_text(By.CSS_SELECTOR, "h1.rich_media_title, #activity-name"),
                'author': self._safe_find_text(By.CSS_SELECTOR, "#js_name, .rich_media_meta_text"),
                'account_name': self._safe_find_text(By.CSS_SELECTOR, "#js_name"),
                'publish_time': self._safe_find_text(By.CSS_SELECTOR, "#publish_time, .rich_media_meta_text"),
                'content': self._safe_find_text(By.ID, "js_content"),
                'read_count': self._extract_read_count(),
                'like_count': self._extract_like_count(),
                'comment_count': self._extract_comment_count(),
                'share_count': self._extract_share_count(),
                'images': self._extract_images(),
                'tags': self._extract_tags(),
                'crawled_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully extracted article: {article_data['title'][:50]}...")
            return article_data
            
        except TimeoutException:
            logger.error(f"Timeout loading article: {article_url}")
            return None
        except Exception as e:
            logger.error(f"Failed to get article content: {e}")
            return None
    
    def _safe_find_text(self, by: By, selector: str) -> str:
        """Safely find element text"""
        try:
            element = self.driver.find_element(by, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _extract_read_count(self) -> str:
        """Extract read count from article"""
        try:
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
        """Extract like count from article"""
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
    
    def _extract_comment_count(self) -> str:
        """Extract comment count from article"""
        try:
            selectors = [
                ".discuss_num",
                "[id*='comment']",
                ".comment_num"
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
    
    def _extract_share_count(self) -> str:
        """Extract share count from article"""
        try:
            selectors = [
                ".share_num",
                "[id*='share']"
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
        """Extract image URLs from article"""
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
    
    def _extract_tags(self) -> List[str]:
        """Extract tags/categories from article"""
        try:
            tags = []
            # Look for tag elements
            tag_elements = self.driver.find_elements(By.CSS_SELECTOR, ".tag, .category, [class*='tag']")
            
            for tag_elem in tag_elements:
                tag_text = tag_elem.text.strip()
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
            
            return tags
        except Exception:
            return []
    
    def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def save_to_csv(self, data: List[Dict], filename: str = None):
        """Save data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_gongzhonghao_{timestamp}.csv"
        
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
        """Save data to JSON file"""
        if not data:
            logger.warning("No data to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wechat_gongzhonghao_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save data to JSON: {e}")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Example usage for WeChat Official Accounts
    crawler = WeChatOfficialAccountsCrawler(headless=True)
    
    try:
        # Search for official accounts
        print("Searching for tech-related official accounts...")
        accounts = crawler.search_official_accounts("人工智能", page=1)
        print(f"Found {len(accounts)} official accounts")
        
        # Get articles from search
        print("Searching for AI-related articles...")
        articles = crawler.search_account_articles("机器学习", page=1)
        print(f"Found {len(articles)} articles")
        
        # Get recent posts from first account if available
        if accounts:
            print(f"Getting recent posts from: {accounts[0]['account_name']}")
            posts = crawler.get_account_recent_posts(accounts[0]['profile_link'], max_posts=3)
            print(f"Found {len(posts)} recent posts")
            
            # Get detailed content for first post
            if posts:
                print(f"Getting detailed content for: {posts[0]['title']}")
                content = crawler.get_article_content(posts[0]['url'])
                if content:
                    print(f"Article title: {content['title']}")
                    print(f"Author: {content['author']}")
                    print(f"Read count: {content['read_count']}")
        
        # Save all data
        all_data = accounts + articles + (posts if 'posts' in locals() else [])
        crawler.save_to_csv(all_data, "wechat_gongzhonghao_data.csv")
        crawler.save_to_json(all_data, "wechat_gongzhonghao_data.json")
        
    finally:
        crawler.close()