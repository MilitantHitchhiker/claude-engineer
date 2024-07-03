from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urlparse
import re

def parse_search_results(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    search_results = []

    for result in soup.select('div.g'):
        title_element = result.select_one('h3')
        url_element = result.select_one('div.yuRUbf > a')
        snippet_element = result.select_one('div.VwiC3b')

        if title_element and url_element:
            title = clean_text(title_element.text)
            url = url_element['href']
            snippet = clean_text(snippet_element.text) if snippet_element else ""

            search_results.append({
                'title': title,
                'url': url,
                'snippet': snippet,
                'domain': extract_domain(url)
            })

    return search_results

def clean_text(text: str) -> str:
    # Remove extra whitespace and newlines
    cleaned = ' '.join(text.split())
    # Remove special characters
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    return cleaned

def extract_domain(url: str) -> str:
    # Extract domain from URL
    return urlparse(url).netloc

def truncate_string(string: str, max_length: int = 100) -> str:
    # Truncate a string to a maximum length
    return string[:max_length] + '...' if len(string) > max_length else string

def remove_duplicates(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # Remove duplicate results based on URL
    seen_urls = set()
    unique_results = []
    for result in results:
        if result['url'] not in seen_urls:
            seen_urls.add(result['url'])
            unique_results.append(result)
    return unique_results

def filter_results(results: List[Dict[str, str]], blacklist_domains: List[str] = None) -> List[Dict[str, str]]:
    # Filter out results from blacklisted domains
    if not blacklist_domains:
        return results
    return [result for result in results if result['domain'] not in blacklist_domains]