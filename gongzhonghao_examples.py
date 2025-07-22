#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Official Accounts (公众号) Crawler Examples
=================================================

Examples showing how to crawl WeChat Official Accounts posts.
"""

import time
from wechat_gongzhonghao_crawler import WeChatOfficialAccountsCrawler


def example_search_tech_accounts():
    """
    Example: Search for technology-related official accounts
    """
    print("=== Search Tech Official Accounts ===")
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        # Search for tech-related accounts
        keywords = ["人工智能", "科技", "互联网", "编程"]
        
        all_accounts = []
        for keyword in keywords:
            print(f"\nSearching for: {keyword}")
            accounts = crawler.search_official_accounts(keyword, page=1)
            
            for account in accounts:
                account['search_keyword'] = keyword
                print(f"Found: {account['account_name']} - {account['description'][:50]}...")
            
            all_accounts.extend(accounts)
            time.sleep(2)  # Be respectful
        
        # Save results
        crawler.save_to_csv(all_accounts, "tech_official_accounts.csv")
        crawler.save_to_json(all_accounts, "tech_official_accounts.json")
        
        print(f"\nTotal accounts found: {len(all_accounts)}")
        return all_accounts


def example_search_articles_by_keyword():
    """
    Example: Search for articles by keyword across all accounts
    """
    print("\n=== Search Articles by Keyword ===")
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        # Search for specific topics
        topics = [
            "ChatGPT",
            "机器学习", 
            "深度学习",
            "Python编程",
            "数据科学"
        ]
        
        all_articles = []
        for topic in topics:
            print(f"\nSearching articles about: {topic}")
            articles = crawler.search_account_articles(topic, page=1)
            
            for article in articles:
                article['search_topic'] = topic
                print(f"Found: {article['title'][:50]}... by {article['account_name']}")
            
            all_articles.extend(articles)
            time.sleep(2)
        
        # Save results
        crawler.save_to_csv(all_articles, "topic_articles.csv")
        
        print(f"\nTotal articles found: {len(all_articles)}")
        return all_articles


def example_crawl_specific_account():
    """
    Example: Get all recent posts from a specific official account
    """
    print("\n=== Crawl Specific Account Posts ===")
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        # First search for a specific account
        account_name = "AI科技大本营"  # Example account name
        accounts = crawler.search_official_accounts(account_name)
        
        if not accounts:
            print(f"Account '{account_name}' not found, trying alternative search...")
            accounts = crawler.search_official_accounts("AI科技")
        
        if accounts:
            account = accounts[0]
            print(f"Found account: {account['account_name']}")
            print(f"Description: {account['description']}")
            
            # Get recent posts
            posts = crawler.get_account_recent_posts(
                account['profile_link'], 
                max_posts=10
            )
            
            print(f"\nRecent posts from {account['account_name']}:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post['title']}")
                print(f"   Date: {post['publish_date']}")
                print(f"   URL: {post['url'][:50]}...")
                print()
            
            # Save results
            crawler.save_to_csv(posts, f"{account['account_name']}_posts.csv")
            
            return posts
        else:
            print("No accounts found")
            return []


def example_get_article_details():
    """
    Example: Get detailed content from specific articles
    """
    print("\n=== Get Article Details ===")
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        # Search for articles first
        articles = crawler.search_account_articles("人工智能发展趋势", page=1)
        
        if articles:
            # Get detailed content for first few articles
            detailed_articles = []
            
            for i, article in enumerate(articles[:3], 1):
                print(f"\nGetting details for article {i}: {article['title'][:50]}...")
                
                content = crawler.get_article_content(article['url'])
                if content:
                    # Merge basic info with detailed content
                    full_article = {**article, **content}
                    detailed_articles.append(full_article)
                    
                    print(f"Title: {content['title']}")
                    print(f"Author: {content['author']}")
                    print(f"Publish time: {content['publish_time']}")
                    print(f"Read count: {content['read_count']}")
                    print(f"Like count: {content['like_count']}")
                    print(f"Content length: {len(content['content'])} characters")
                    print(f"Images: {len(content['images'])} found")
                
                time.sleep(3)  # Respectful delay
            
            # Save detailed articles
            crawler.save_to_json(detailed_articles, "detailed_articles.json")
            
            return detailed_articles
        else:
            print("No articles found")
            return []


def example_monitor_trending_topics():
    """
    Example: Monitor trending topics in WeChat Official Accounts
    """
    print("\n=== Monitor Trending Topics ===")
    
    # Trending topics to monitor
    trending_topics = [
        "OpenAI",
        "GPT-4", 
        "自动驾驶",
        "区块链",
        "元宇宙",
        "量子计算",
        "5G技术",
        "新能源"
    ]
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        trending_data = []
        
        for topic in trending_topics:
            print(f"\nMonitoring topic: {topic}")
            
            # Search for recent articles about this topic
            articles = crawler.search_account_articles(topic, page=1)
            
            topic_data = {
                'topic': topic,
                'article_count': len(articles),
                'articles': articles,
                'monitored_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            trending_data.append(topic_data)
            
            print(f"Found {len(articles)} articles about {topic}")
            
            # Show top 3 articles
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article['title'][:60]}...")
                print(f"     by {article['account_name']} | {article['publish_date']}")
            
            time.sleep(2)
        
        # Save trending analysis
        crawler.save_to_json(trending_data, "trending_topics_analysis.json")
        
        # Create summary
        summary = []
        for topic_data in trending_data:
            summary.append({
                'topic': topic_data['topic'],
                'article_count': topic_data['article_count'],
                'monitored_at': topic_data['monitored_at']
            })
        
        crawler.save_to_csv(summary, "trending_topics_summary.csv")
        
        return trending_data


def example_batch_account_analysis():
    """
    Example: Analyze multiple accounts in batch
    """
    print("\n=== Batch Account Analysis ===")
    
    # Industries to analyze
    industries = {
        "科技": ["科技", "技术", "互联网"],
        "金融": ["金融", "投资", "理财"],  
        "教育": ["教育", "学习", "培训"],
        "健康": ["健康", "医疗", "养生"],
        "创业": ["创业", "商业", "企业"]
    }
    
    with WeChatOfficialAccountsCrawler(headless=True) as crawler:
        industry_analysis = {}
        
        for industry, keywords in industries.items():
            print(f"\nAnalyzing {industry} industry...")
            
            industry_accounts = []
            industry_articles = []
            
            for keyword in keywords:
                # Get accounts
                accounts = crawler.search_official_accounts(keyword, page=1)
                for account in accounts:
                    account['industry'] = industry
                    account['keyword'] = keyword
                industry_accounts.extend(accounts)
                
                # Get articles  
                articles = crawler.search_account_articles(keyword, page=1)
                for article in articles:
                    article['industry'] = industry
                    article['keyword'] = keyword
                industry_articles.extend(articles)
                
                time.sleep(1)
            
            industry_analysis[industry] = {
                'accounts': industry_accounts,
                'articles': industry_articles,
                'account_count': len(industry_accounts),
                'article_count': len(industry_articles)
            }
            
            print(f"{industry}: {len(industry_accounts)} accounts, {len(industry_articles)} articles")
        
        # Save analysis results
        for industry, data in industry_analysis.items():
            crawler.save_to_csv(data['accounts'], f"{industry}_accounts.csv")
            crawler.save_to_csv(data['articles'], f"{industry}_articles.csv")
        
        # Create overall summary
        summary = []
        for industry, data in industry_analysis.items():
            summary.append({
                'industry': industry,
                'account_count': data['account_count'],
                'article_count': data['article_count'],
                'analyzed_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        crawler.save_to_csv(summary, "industry_analysis_summary.csv")
        
        return industry_analysis


if __name__ == "__main__":
    print("WeChat Official Accounts (公众号) Crawler Examples")
    print("=" * 55)
    
    try:
        # Run examples (uncomment the ones you want to test)
        
        # Example 1: Search for tech accounts
        accounts = example_search_tech_accounts()
        
        # Example 2: Search articles by keyword
        # articles = example_search_articles_by_keyword()
        
        # Example 3: Crawl specific account
        # posts = example_crawl_specific_account()
        
        # Example 4: Get article details
        # detailed = example_get_article_details()
        
        # Example 5: Monitor trending topics
        # trending = example_monitor_trending_topics()
        
        # Example 6: Batch analysis
        # analysis = example_batch_account_analysis()
        
        print("\n" + "=" * 55)
        print("Examples completed! Check the generated files for results.")
        print("Note: Some examples are commented out to avoid overwhelming")
        print("the demo. Uncomment them to run specific examples.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have all required dependencies installed.")
        print("Try: pip install -r requirements.txt")