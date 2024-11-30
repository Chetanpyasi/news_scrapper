import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_database"
COLLECTION_NAME = "indian_express_articles"

# Connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return collection

# Function to extract article content and upload to MongoDB
def extract_and_upload_article(article_url, collection):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title_tag = soup.find('h1')  # Adjust if the title uses a different tag
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Group content by tags with additional details
        content_data = {}
        content_tags = soup.find_all(['p', 'h2', 'h3', 'li', 'img'])  # Add more tags if needed
        for tag in content_tags:
            tag_name = tag.name
            # Extract details
            text = tag.get_text(strip=True) if tag_name != 'img' else None
            src = tag.get('src') if tag_name == 'img' else None
            alt = tag.get('alt') if tag_name == 'img' else None
            class_attr = tag.get('class', [])
            
            # Prepare content item
            content_item = {
                "text": text,
                "src": src,
                "alt": alt,
                "class": class_attr
            }

            # Add to grouped data
            if tag_name not in content_data:
                content_data[tag_name] = []
            content_data[tag_name].append(content_item)

        # Prepare the article data
        article_data = {
            "url": article_url,
            "title": title,
            "content": content_data
        }

        # Insert the article into MongoDB
        collection.insert_one(article_data)
        print(f"Inserted article: {title}")

    except Exception as e:
        print(f"Error while extracting article from {article_url}: {e}")

# Function to scrape the Indian Express homepage and process each article
def scrape_indian_express_homepage(url, collection):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links to news articles
        article_links = soup.find_all('a', href=True)  # Adjust selectors if needed
        base_url = "https://indianexpress.com"
        
        for link in article_links:
            article_url = link['href']
            if not article_url.startswith("http"):
                article_url = base_url + article_url

            print(f"Scraping article: {article_url}")
            extract_and_upload_article(article_url, collection)

    except Exception as e:
        print(f"Error occurred while scraping homepage: {e}")

# Main function
if __name__ == "__main__":
    homepage_url = "https://timesofindia.indiatimes.com/"  # Replace with the correct homepage URL
    news_collection = connect_to_mongodb()
    scrape_indian_express_homepage(homepage_url, news_collection)
