import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def get_all_links(url, base_url, visited):
    """
    Retrieves all the links from a given URL.

    Args:
        url (str): The URL to retrieve the links from.
        base_url (str): The base URL of the website.
        visited (set): A set of visited URLs.

    Returns:
        set: A set of all the links found on the page.

    Raises:
        requests.RequestException: If there is an error fetching the URL.

    This function uses the `requests` library to send a GET request to the given URL. It then parses the HTML content of the response using BeautifulSoup. It finds all the anchor tags with the `href` attribute and extracts the link by joining it with the base URL. It checks if the link starts with the base URL and has not been visited before, and if so, adds it to the set of links.

    If there is an error fetching the URL, it prints an error message with the URL and the exception.
    """
    links = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for anchor in soup.find_all("a", href=True):
            link = urljoin(base_url, anchor["href"])
            if link.startswith(base_url) and link not in visited:
                links.add(link)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return links

def extract_paragraphs(url):
    """
    Extracts all the paragraphs from a given URL.

    Args:
        url (str): The URL of the website to extract paragraphs from.

    Returns:
        list: A list of strings, where each string represents a paragraph extracted from the website.

    Raises:
        requests.RequestException: If there is an error fetching the URL.
    """
    paragraphs = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for paragraph in soup.find_all("p"):
            paragraphs.append(paragraph.get_text())
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return paragraphs

def crawl_website(start_url):
    """
    Crawls a website starting from a given URL and extracts all the paragraphs from the pages.

    Parameters:
    - start_url (str): The URL of the website to start crawling from.

    Returns:
    - all_paragraphs (List[str]): A list of all the paragraphs extracted from the website.

    The function starts by initializing the base URL of the website, a set of URLs to visit, a set of visited URLs, and an empty list to store all the paragraphs. It then enters a loop where it continues until there are no more URLs to visit.

    For each URL in the set of URLs to visit, the function checks if it has already been visited. If not, it adds the URL to the set of visited URLs, retrieves all the links from the current URL, updates the set of URLs to visit with the new links, extracts the paragraphs from the current URL, and adds them to the list of all paragraphs.

    The function uses the `get_all_links` function to retrieve all the links from a given URL. It uses the `extract_paragraphs` function to extract the paragraphs from a given URL.

    The function sleeps for 1 second between each request to avoid overwhelming the server.

    Finally, the function returns the list of all the paragraphs extracted from the website.
    """
    base_url = "{0.scheme}://{0.netloc}".format(urlparse(start_url))
    to_visit = {start_url}
    visited = set()
    all_paragraphs = []

    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited:
            visited.add(current_url)
            new_links = get_all_links(current_url, base_url, visited)
            to_visit.update(new_links)
            paragraphs = extract_paragraphs(current_url)
            all_paragraphs.extend(paragraphs)
            time.sleep(1)  # Be polite and avoid overwhelming the server

    return all_paragraphs

# Specify the starting URL
start_url = "https://www.digitalrhombusstudios.com"
all_paragraphs = crawl_website(start_url)

# Save the paragraphs to a text file
with open("website_paragraphs.txt", "w", encoding="utf-8") as file:
    for paragraph in all_paragraphs:
        file.write(f"{paragraph}\n\n")

print(f"Total {len(all_paragraphs)} paragraphs saved to website_paragraphs.txt")
