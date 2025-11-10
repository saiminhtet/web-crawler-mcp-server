import asyncio
import json
from typing import List, Dict, Any, Optional
import aiohttp
from newspaper import Article, Config
from newspaper.article import ArticleException
import feedparser
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebCrawlerTools:
    def __init__(self):
        self.session = None
        # Configure newspaper4k
        self.article_config = Config()
        self.article_config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.article_config.request_timeout = 10

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def crawl_news_article(self, url: str, language: str = 'en') -> str:
        """
        Extract and parse news articles using newspaper4k library.
        
        Args:
            url: The URL of the news article to crawl
            language: Language of the article (default: 'en')
        
        Returns:
            JSON string containing article title, text, authors, publish date, etc.
        """
        try:
            logger.info(f"Crawling news article: {url}")
            
            # Create article object
            article = Article(url, config=self.article_config, language=language)
            
            # Download and parse
            article.download()
            article.parse()
            article.nlp()  # Perform natural language processing
            
            result = {
                'url': url,
                'title': article.title,
                'text': article.text,
                'summary': article.summary,
                'keywords': article.keywords,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'top_image': article.top_image,
                'images': list(article.images),
                'movies': article.movies,
                'meta_description': article.meta_description,
                'meta_lang': article.meta_lang,
                'meta_favicon': article.meta_favicon,
                'meta_keywords': article.meta_keywords,
                'canonical_link': article.canonical_link,
                'success': True
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except ArticleException as e:
            error_result = {
                'url': url,
                'success': False,
                'error': f"Newspaper4k error: {str(e)}"
            }
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {
                'url': url,
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
            return json.dumps(error_result, indent=2)

    async def extract_multiple_news_articles(self, urls: List[str], language: str = 'en') -> str:
        """
        Extract multiple news articles at once.
        
        Args:
            urls: List of URLs to crawl
            language: Language of the articles (default: 'en')
        
        Returns:
            JSON string containing results for all articles
        """
        results = []
        
        for url in urls:
            try:
                article_result = await self.crawl_news_article(url, language)
                results.append(json.loads(article_result))
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return json.dumps(results, indent=2, default=str)

    async def discover_news_from_rss(self, rss_url: str, max_articles: int = 10) -> str:
        """
        Discover news articles from RSS feeds and extract their content.
        
        Args:
            rss_url: URL of the RSS feed
            max_articles: Maximum number of articles to extract (default: 10)
        
        Returns:
            JSON string containing discovered articles with full content
        """
        try:
            logger.info(f"Parsing RSS feed: {rss_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                results = []
                articles_to_process = min(max_articles, len(feed.entries))
                
                for i, entry in enumerate(feed.entries[:articles_to_process]):
                    if hasattr(entry, 'link'):
                        logger.info(f"Processing article {i+1}/{articles_to_process}: {entry.link}")
                        
                        # Extract full article content
                        article_data = await self.crawl_news_article(entry.link)
                        article_json = json.loads(article_data)
                        
                        # Add RSS metadata
                        article_json['rss_title'] = entry.title if hasattr(entry, 'title') else None
                        article_json['rss_published'] = entry.published if hasattr(entry, 'published') else None
                        article_json['rss_summary'] = entry.summary if hasattr(entry, 'summary') else None
                        
                        results.append(article_json)
                    
                    # Small delay to be respectful to the server
                    await asyncio.sleep(1)
                
                return json.dumps(results, indent=2, default=str)
            else:
                return json.dumps({
                    'success': False,
                    'error': 'No entries found in RSS feed',
                    'rss_url': rss_url
                }, indent=2)
                
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': f"RSS parsing error: {str(e)}",
                'rss_url': rss_url
            }, indent=2)

    async def search_and_extract_news(self, query: str, rss_feeds: List[str] = None, max_results: int = 5) -> str:
        """
        Search for news across multiple RSS feeds and extract content.
        
        Args:
            query: Search query to look for in news articles
            rss_feeds: List of RSS feed URLs to search (default: common news feeds)
            max_results: Maximum number of results to return
        
        Returns:
            JSON string containing matching articles with full content
        """
        # Default RSS feeds if none provided
        if rss_feeds is None:
            rss_feeds = [
                'http://rss.cnn.com/rss/edition.rss',
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
            ]
        
        all_articles = []
        
        for rss_feed in rss_feeds:
            try:
                feed_articles = await self.discover_news_from_rss(rss_feed, max_results)
                articles_data = json.loads(feed_articles)
                
                if isinstance(articles_data, list):
                    all_articles.extend(articles_data)
            except Exception as e:
                logger.error(f"Error processing RSS feed {rss_feed}: {e}")
        
        # Filter articles based on search query
        query_lower = query.lower()
        matching_articles = []
        
        for article in all_articles:
            if (article.get('success') and 
                (query_lower in article.get('title', '').lower() or 
                 query_lower in article.get('text', '').lower() or
                 query_lower in article.get('summary', '').lower())):
                matching_articles.append(article)
        
        return json.dumps(matching_articles[:max_results], indent=2, default=str)

    async def get_news_summary(self, url: str, summary_length: int = 5) -> str:
        """
        Get a summarized version of a news article with key points.
        
        Args:
            url: URL of the news article
            summary_length: Number of sentences for the summary (default: 5)
        
        Returns:
            JSON string containing article summary and key information
        """
        try:
            article_data = await self.crawl_news_article(url)
            article_json = json.loads(article_data)
            
            if article_json.get('success'):
                # Use newspaper4k's built-in summary or create our own
                summary = article_json.get('summary', '')
                if not summary:
                    # Fallback: take first few sentences
                    sentences = article_json.get('text', '').split('. ')
                    summary = '. '.join(sentences[:summary_length]) + '.'
                
                result = {
                    'url': url,
                    'title': article_json.get('title'),
                    'summary': summary,
                    'keywords': article_json.get('keywords', [])[:10],  # Top 10 keywords
                    'authors': article_json.get('authors'),
                    'publish_date': article_json.get('publish_date'),
                    'top_image': article_json.get('top_image'),
                    'success': True
                }
                
                return json.dumps(result, indent=2, default=str)
            else:
                return article_data
                
        except Exception as e:
            return json.dumps({
                'url': url,
                'success': False,
                'error': f"Summary extraction error: {str(e)}"
            }, indent=2)