import asyncio
import logging
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools import WebCrawlerTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize tools
crawler_tools = WebCrawlerTools()

# Create MCP server
server = Server("web-crawler-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="crawl_news_article",
            description="Extract and parse news articles using newspaper4k library",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the news article to crawl"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language of the article",
                        "default": "en"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="extract_multiple_news_articles",
            description="Extract multiple news articles at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to crawl"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language of the articles",
                        "default": "en"
                    }
                },
                "required": ["urls"]
            }
        ),
        Tool(
            name="discover_news_from_rss",
            description="Discover news articles from RSS feeds and extract their content",
            inputSchema={
                "type": "object",
                "properties": {
                    "rss_url": {
                        "type": "string",
                        "description": "URL of the RSS feed"
                    },
                    "max_articles": {
                        "type": "integer",
                        "description": "Maximum number of articles to extract",
                        "default": 10
                    }
                },
                "required": ["rss_url"]
            }
        ),
        Tool(
            name="search_and_extract_news",
            description="Search for news across multiple RSS feeds and extract content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to look for in news articles"
                    },
                    "rss_feeds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of RSS feed URLs to search"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_news_summary",
            description="Get a summarized version of a news article with key points",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the news article"
                    },
                    "summary_length": {
                        "type": "integer",
                        "description": "Number of sentences for the summary",
                        "default": 5
                    }
                },
                "required": ["url"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "crawl_news_article":
            result = await crawler_tools.crawl_news_article(
                arguments.get("url"),
                arguments.get("language", "en")
            )
        elif name == "extract_multiple_news_articles":
            result = await crawler_tools.extract_multiple_news_articles(
                arguments.get("urls"),
                arguments.get("language", "en")
            )
        elif name == "discover_news_from_rss":
            result = await crawler_tools.discover_news_from_rss(
                arguments.get("rss_url"),
                arguments.get("max_articles", 10)
            )
        elif name == "search_and_extract_news":
            result = await crawler_tools.search_and_extract_news(
                arguments.get("query"),
                arguments.get("rss_feeds"),
                arguments.get("max_results", 5)
            )
        elif name == "get_news_summary":
            result = await crawler_tools.get_news_summary(
                arguments.get("url"),
                arguments.get("summary_length", 5)
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_result = json.dumps({
            "success": False,
            "error": str(e)
        })
        return [TextContent(type="text", text=error_result)]

async def main():
    """Main function to run the MCP server"""

    logger.info("Starting Web Crawler MCP Server...")

    try:
        # Initialize session
        await crawler_tools.init_session()

        # Run the server using stdio
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Cleanup
        await crawler_tools.close_session()

if __name__ == "__main__":
    asyncio.run(main())