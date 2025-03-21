import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_and_parse_html(url):
    """
    Fetches the HTML for given URL and parses using BeautifulSoup.
    
    Returns:
        soup (BeautifulSoup): The parsed HTML.
        base_url (str): The base URL of the webpage.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        return soup, base_url
    
    except Exception as e:
        raise Exception(f"Failed to fetch or parse given website {e}")
