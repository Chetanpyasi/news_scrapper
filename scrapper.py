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

# Function to extract article content
def extract_article_content(article_url):
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

        # Extract content with tags
        content_data = []
        content_tags = soup.find_all(['p', 'h2', 'h3', 'li', 'img'])  # Add more tags if needed
        for tag in content_tags:
            content_item = {
                "tag": tag.name,
                "content": tag.get_text(strip=True) if tag.name != 'img' else tag.get('src', 'No Image')
            }
            content_data.append(content_item)

        return {"title": title, "content": content_data}

    except Exception as e:
        print(f"Error while extracting article: {e}")
        return None

# Function to scrape the Indian Express homepage
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
        scraped_data = []

        for link in article_links:
            article_url = link['href']
            if not article_url.startswith("http"):
                article_url = base_url + article_url

            print(f"Scraping article: {article_url}")
            article_content = extract_article_content(article_url)
            if article_content:
                scraped_data.append({
                    "url": article_url,
                    "title": article_content['title'],
                    "content": article_content['content']
                })

        # Insert data into MongoDB
        if scraped_data:
            collection.insert_many(scraped_data)
            print(f"Inserted {len(scraped_data)} articles into the database.")
        else:
            print("No articles found to insert.")

    except Exception as e:
        print(f"Error occurred: {e}")

# Main function
if __name__ == "__main__":
    homepage_url = "https://indianexpress.com/"  # Replace with the correct homepage URL
    news_collection = connect_to_mongodb()
    scrape_indian_express_homepage(homepage_url, news_collection)
