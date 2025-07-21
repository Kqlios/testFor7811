#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Crawler Usage Examples
============================

This file demonstrates various ways to use the WeChat crawler.
"""

import asyncio
import time
from wechat_crawler import WeChatCrawler, AsyncWeChatCrawler


def example_basic_crawling():
    """
    Basic example of crawling WeChat posts
    """
    print("=== Basic WeChat Crawling Example ===")
    
    # Initialize crawler
    crawler = WeChatCrawler(headless=True)
    
    try:
        # Search for tech-related WeChat accounts
        print("Searching for technology-related WeChat accounts...")
        accounts = crawler.search_wechat_accounts("人工智能", page=1)
        print(f"Found {len(accounts)} accounts")
        
        if accounts:
            # Display account information
            for i, account in enumerate(accounts[:3], 1):
                print(f"\nAccount {i}:")
                print(f"  Name: {account['account_name']}")
                print(f"  WeChat ID: {account['wechat_id']}")
                print(f"  Description: {account['description'][:100]}...")
            
            # Get posts from the first account
            first_account = accounts[0]
            print(f"\nGetting posts from: {first_account['account_name']}")
            
            posts = crawler.get_account_posts(
                first_account['profile_link'], 
                max_posts=3
            )
            
            print(f"Found {len(posts)} posts")
            
            # Display post information
            for i, post in enumerate(posts, 1):
                print(f"\nPost {i}:")
                print(f"  Title: {post['title']}")
                print(f"  Date: {post['publish_date']}")
                print(f"  Description: {post['description'][:100]}...")
            
            # Get detailed content for the first post
            if posts:
                print(f"\nGetting detailed content for: {posts[0]['title']}")
                content = crawler.get_post_content(posts[0]['link'])
                
                if content:
                    print(f"Title: {content['title']}")
                    print(f"Author: {content['author']}")
                    print(f"Publish Time: {content['publish_time']}")
                    print(f"Read Count: {content['read_count']}")
                    print(f"Like Count: {content['like_count']}")
                    print(f"Content Length: {len(content['content'])} characters")
                    print(f"Images: {len(content['images'])} found")
            
            # Save all data
            print("\nSaving data to files...")
            crawler.save_to_csv(posts, "example_posts.csv")
            crawler.save_to_json(posts, "example_posts.json")
            print("Data saved successfully!")
        
        else:
            print("No accounts found. Try different keywords.")
    
    except Exception as e:
        print(f"Error during crawling: {e}")
    
    finally:
        crawler.close()


def example_batch_crawling():
    """
    Example of crawling multiple accounts in batch
    """
    print("\n=== Batch Crawling Example ===")
    
    keywords = ["科技", "教育", "健康"]
    all_posts = []
    
    crawler = WeChatCrawler(headless=True)
    
    try:
        for keyword in keywords:
            print(f"\nSearching for keyword: {keyword}")
            accounts = crawler.search_wechat_accounts(keyword, page=1)
            
            for account in accounts[:2]:  # Top 2 accounts per keyword
                print(f"Getting posts from: {account['account_name']}")
                posts = crawler.get_account_posts(
                    account['profile_link'], 
                    max_posts=2
                )
                
                # Add keyword tag to each post
                for post in posts:
                    post['search_keyword'] = keyword
                    post['account_name'] = account['account_name']
                
                all_posts.extend(posts)
                time.sleep(2)  # Be respectful to servers
        
        print(f"\nTotal posts collected: {len(all_posts)}")
        
        # Save all collected posts
        crawler.save_to_csv(all_posts, "batch_crawled_posts.csv")
        crawler.save_to_json(all_posts, "batch_crawled_posts.json")
        
    except Exception as e:
        print(f"Error during batch crawling: {e}")
    
    finally:
        crawler.close()


async def example_async_crawling():
    """
    Example of asynchronous crawling for better performance
    """
    print("\n=== Async Crawling Example ===")
    
    # Sample WeChat post URLs (you would get these from account crawling)
    sample_urls = [
        "https://mp.weixin.qq.com/s/sample_url_1",
        "https://mp.weixin.qq.com/s/sample_url_2",
        "https://mp.weixin.qq.com/s/sample_url_3",
    ]
    
    async_crawler = AsyncWeChatCrawler(max_concurrent=3)
    
    try:
        print("Starting async crawling of multiple posts...")
        start_time = time.time()
        
        posts = await async_crawler.batch_crawl_posts(sample_urls)
        
        end_time = time.time()
        print(f"Crawled {len(posts)} posts in {end_time - start_time:.2f} seconds")
        
        for i, post in enumerate(posts, 1):
            print(f"Post {i}: {post['title'][:50]}...")
    
    except Exception as e:
        print(f"Error during async crawling: {e}")


def example_with_proxy():
    """
    Example of using the crawler with a proxy
    """
    print("\n=== Proxy Usage Example ===")
    
    # Note: Replace with your actual proxy URL
    proxy_url = "http://your-proxy-server:port"
    
    try:
        crawler = WeChatCrawler(
            headless=True,
            proxy=proxy_url  # Only if you have a proxy
        )
        
        print("Crawler initialized with proxy")
        print("Searching with proxy...")
        
        accounts = crawler.search_wechat_accounts("新闻", page=1)
        print(f"Found {len(accounts)} accounts using proxy")
        
        crawler.close()
        
    except Exception as e:
        print(f"Proxy example error (expected if no proxy configured): {e}")


def example_custom_search():
    """
    Example of custom search with specific parameters
    """
    print("\n=== Custom Search Example ===")
    
    crawler = WeChatCrawler(headless=False)  # Non-headless for demo
    
    try:
        # Search for specific topics
        topics = ["机器学习", "深度学习", "自然语言处理"]
        
        for topic in topics:
            print(f"\nSearching for: {topic}")
            accounts = crawler.search_wechat_accounts(topic, page=1)
            
            if accounts:
                # Get detailed info for first account
                account = accounts[0]
                print(f"Top result: {account['account_name']}")
                print(f"Description: {account['description']}")
                
                # Get recent posts
                posts = crawler.get_account_posts(
                    account['profile_link'],
                    max_posts=1
                )
                
                if posts:
                    post = posts[0]
                    print(f"Latest post: {post['title']}")
                    
                    # Get full content
                    content = crawler.get_post_content(post['link'])
                    if content:
                        print(f"Full content available: {len(content['content'])} chars")
    
    except Exception as e:
        print(f"Custom search error: {e}")
    
    finally:
        crawler.close()


if __name__ == "__main__":
    print("WeChat Crawler Usage Examples")
    print("=" * 40)
    
    # Run basic example
    example_basic_crawling()
    
    # Run batch example
    example_batch_crawling()
    
    # Run async example
    # asyncio.run(example_async_crawling())
    
    # Run proxy example (will fail without actual proxy)
    # example_with_proxy()
    
    # Run custom search example
    # example_custom_search()
    
    print("\nAll examples completed!")
    print("Check the generated CSV and JSON files for results.")