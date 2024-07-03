# Scraper Configuration

# Number of agents to use for scraping
NUM_AGENTS = 5

# Maximum number of results to fetch per query
MAX_RESULTS_PER_QUERY = 10

# Search engine URL (Google in this case)
SEARCH_ENGINE_URL = "https://www.google.com/search?q={query}&num=100"

# User agent string for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Delay between requests (in seconds) to avoid rate limiting
REQUEST_DELAY = 2

# Timeout for requests (in seconds)
REQUEST_TIMEOUT = 15

# List of default search queries
DEFAULT_SEARCH_QUERIES = [
    "artificial intelligence",
    "machine learning",
    "natural language processing",
    "computer vision",
    "robotics"
]

# Blacklisted domains (example)
BLACKLIST_DOMAINS = [
    "example.com",
    "spam-site.com"
]

# Maximum retries for failed requests
MAX_RETRIES = 3

# Proxy settings (if needed)
USE_PROXY = False
PROXY_URL = "http://your-proxy-url:port"

# Output file name
OUTPUT_FILE = "search_results.json"