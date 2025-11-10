# Web Crawler MCP Server

A Model Context Protocol (MCP) server for web crawling and news article extraction. This server enables LLMs to browse the web, extract article content using newspaper4k, and process RSS feeds with structured data output.

## Features

- 📰 Extract full news articles with metadata (title, authors, publish date, content)
- 🔍 Discover and process content from RSS feeds
- 🎯 Smart content parsing using newspaper4k library
- ⚡ Batch URL processing with concurrent requests
- 🔄 Real-time web access for LLM applications
- 🤖 Full MCP SDK compliance for seamless integration

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
# Clone the repository
cd web-crawler-mcp-server

# Install required packages
pip install -r requirements.txt

# Or using pyproject.toml
pip install -e .
```

### Required Packages

- `mcp>=1.0.0` - Model Context Protocol SDK
- `newspaper4k>=0.2.8` - News article extraction
- `beautifulsoup4>=4.12.0` - HTML parsing
- `aiohttp>=3.9.0` - Async HTTP client
- `feedparser>=6.0.0` - RSS feed parsing
- `lxml>=4.9.0` - XML processing
- `lxml_html_clean>=0.4.0` - HTML cleaning for lxml (required by newspaper4k)

## Configuration

### Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration (recommended - using home directory shortcut):**
```json
{
  "mcpServers": {
    "web-crawler": {
      "command": "/Users/saiminhtet/web-crawler-mcp-server/venv/bin/python",
      "args": ["-m", "web_crawler_mcp.server"]
    }
  }
}
```

**Alternative Configuration (generic template):**
```json
{
  "mcpServers": {
    "web-crawler": {
      "command": "/absolute/path/to/web-crawler-mcp-server/venv/bin/python",
      "args": ["-m", "web_crawler_mcp.server"]
    }
  }
}
```

**Important Notes:**
- Use the virtual environment's Python (in `venv/bin/python`) not system Python
- The module name is `web_crawler_mcp.server` (no `src.` prefix when installed)
- Use **absolute paths** (not `~` or relative paths)
- If your path contains spaces or special characters, create a symlink: `ln -sf "/path/with/spaces" ~/web-crawler-mcp-server`
- On Windows, use `venv\Scripts\python.exe` instead of `venv/bin/python`
- After updating the config, restart Claude Desktop

**Windows Example:**
```json
{
  "mcpServers": {
    "web-crawler": {
      "command": "C:\\Users\\YourName\\web-crawler-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["-m", "web_crawler_mcp.server"]
    }
  }
}
```

**Troubleshooting Path Issues:**

If you get JSON parse errors with special characters in your path:
```bash
# Create a symlink without special characters
ln -sf "/Users/saiminhtet/Research&Development/python/ai-development/web-crawler-mcp-server" ~/web-crawler-mcp-server

# Then use the symlink path in your config:
# /Users/saiminhtet/web-crawler-mcp-server/venv/bin/python
```

### Setup Steps

1. **Create and activate virtual environment:**
```bash
cd /path/to/web-crawler-mcp-server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install the package:**
```bash
pip install -e .
```

3. **Update Claude Desktop config** (see configuration above)

4. **Restart Claude Desktop**

### Other MCP Clients

Run the server directly from the virtual environment:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the server
python -m web_crawler_mcp.server
```

The server communicates via stdio and follows the MCP protocol specification.

## Available Tools

### 1. `crawl_news_article`

Extract and parse a single news article with full metadata.

**Parameters:**
- `url` (string, required): The URL of the news article to crawl
- `language` (string, optional): Language of the article (default: "en")

**Returns:** JSON with article details including title, text, summary, keywords, authors, publish date, images, and metadata.

**Example:**
```json
{
  "url": "https://example.com/article",
  "language": "en"
}
```

### 2. `extract_multiple_news_articles`

Extract multiple news articles at once with batch processing.

**Parameters:**
- `urls` (array of strings, required): List of URLs to crawl
- `language` (string, optional): Language of the articles (default: "en")

**Returns:** JSON array with results for all articles.

**Example:**
```json
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ],
  "language": "en"
}
```

### 3. `discover_news_from_rss`

Discover and extract news articles from RSS feeds.

**Parameters:**
- `rss_url` (string, required): URL of the RSS feed
- `max_articles` (integer, optional): Maximum number of articles to extract (default: 10)

**Returns:** JSON array of articles with RSS metadata and full content.

**Example:**
```json
{
  "rss_url": "http://rss.cnn.com/rss/edition.rss",
  "max_articles": 5
}
```

### 4. `search_and_extract_news`

Search for news across multiple RSS feeds and extract matching content.

**Parameters:**
- `query` (string, required): Search query to look for in news articles
- `rss_feeds` (array of strings, optional): List of RSS feed URLs to search
- `max_results` (integer, optional): Maximum number of results to return (default: 5)

**Returns:** JSON array of matching articles with full content.

**Example:**
```json
{
  "query": "artificial intelligence",
  "rss_feeds": [
    "http://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml"
  ],
  "max_results": 5
}
```

### 5. `get_news_summary`

Get a summarized version of a news article with key points.

**Parameters:**
- `url` (string, required): URL of the news article
- `summary_length` (integer, optional): Number of sentences for the summary (default: 5)

**Returns:** JSON with article summary, title, keywords, authors, and key metadata.

**Example:**
```json
{
  "url": "https://example.com/article",
  "summary_length": 5
}
```

## Usage Examples

Once configured, you can use the server through your MCP client:

```
"Crawl the latest news from https://example.com/article and summarize it"

"Extract articles from the CNN RSS feed and find stories about technology"

"Get summaries of these 3 articles: [URL1, URL2, URL3]"

"Search for AI-related news across BBC and Reuters RSS feeds"
```

## Response Format

All tools return JSON responses with consistent structure:

**Success Response:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "text": "Full article text...",
  "summary": "Article summary...",
  "keywords": ["keyword1", "keyword2"],
  "authors": ["Author Name"],
  "publish_date": "2025-01-15",
  "top_image": "https://example.com/image.jpg",
  "images": ["image1.jpg", "image2.jpg"],
  "meta_description": "Article description",
  "success": true
}
```

**Error Response:**
```json
{
  "url": "https://example.com/article",
  "success": false,
  "error": "Error description"
}
```

## Common RSS Feeds for Testing

- **CNN**: http://rss.cnn.com/rss/edition.rss
- **BBC News**: https://feeds.bbci.co.uk/news/rss.xml
- **New York Times**: https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
- **Reuters Business**: https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best

## Best Practices

### Rate Limiting
The server implements delays between requests (1 second) to be respectful to websites. Adjust `asyncio.sleep()` values in `tools.py` as needed.

### Robots.txt
Always respect robots.txt directives when crawling websites.

### Error Handling
All tools include robust error handling for network issues, parsing errors, and invalid URLs.

### Memory Management
The server processes articles sequentially to manage memory usage. For large batch operations, consider implementing pagination.

### User Agent
The server uses a standard browser user agent to avoid being blocked:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## Development

### Project Structure

```
web-crawler-mcp-server/
├── src/
│   └── web_crawler_mcp/
│       ├── __init__.py
│       ├── server.py        # MCP server implementation
│       └── tools.py          # Web crawler tools
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Test individual article crawling
python -c "
import asyncio
from src.web_crawler_mcp.tools import WebCrawlerTools

async def test():
    tools = WebCrawlerTools()
    await tools.init_session()
    result = await tools.crawl_news_article('https://example.com/article')
    print(result)
    await tools.close_session()

asyncio.run(test())
"
```

## Troubleshooting

### Import Errors
Ensure all dependencies are installed: `pip install -r requirements.txt`

### Connection Timeouts
Adjust `request_timeout` in `tools.py` WebCrawlerTools initialization (default: 10 seconds)

### Article Parsing Fails
Some websites may block automated crawlers. Try adjusting the user agent or use alternative sources.

### RSS Feed Errors
Verify the RSS feed URL is valid and accessible. Some feeds may require authentication.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Author

Sai Min Htet (saiminhtet@u.nus.edu)

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [newspaper4k](https://github.com/AndyTheFactory/newspaper4k) for article extraction
- Powered by the Model Context Protocol