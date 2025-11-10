import asyncio
import json
from src.web_crawler_mcp.tools import WebCrawlerTools

async def test_crawler():
    crawler = WebCrawlerTools()
    await crawler.init_session()
    
    try:
        # Test news article extraction
        print("Testing news article extraction...")
        result = await crawler.crawl_news_article("https://www.bbc.com/news/articles/cy40q990g28o")
        print("Article extraction result:")
        print(result)
        
        # Test RSS feed
        print("\nTesting RSS feed...")
        # rss_result = await crawler.discover_news_from_rss("http://rss.cnn.com/rss/edition.rss", 2)
        # print("RSS result:")
        # print(rss_result)
        
    finally:
        await crawler.close_session()

if __name__ == "__main__":
    asyncio.run(test_crawler())