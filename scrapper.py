import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_database"
COLLECTION_NAME = "indian_express_articles"

# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return collection

# Function to scrape Indian Express
def scrape_indian_express(url, collection):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        # Fetch the webpage content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all news containers
        news_containers = soup.find_all('div', class_='articles')  # Update based on structure

        scraped_data = []

        for news in news_containers:
            # Extract title
            title_tag = news.find('h2', class_='title')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # Extract description
            description_tag = news.find('p')
            description = description_tag.get_text(strip=True) if description_tag else "No Description"

            # Extract article URL
            link_tag = news.find('a', href=True)
            article_url = link_tag['href'] if link_tag else "No URL"

            # Extract image URL
            image_tag = news.find('img')
            image = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "No Image"

            # Prepare a dictionary for MongoDB
            news_item = {
                "title": title,
                "description": description,
                "url": article_url,
                "image": image
            }
            scraped_data.append(news_item)

        # Insert scraped data into MongoDB
        if scraped_data:
            collection.insert_many(scraped_data)
            print(f"Inserted {len(scraped_data)} articles into the database.")
        else:
            print("No articles found to insert.")

    except Exception as e:
        print(f"Error occurred: {e}")


def scrape_multiple_pages(base_url, collection, max_pages=5):
    for page in range(1, max_pages + 1):
        page_url = f"{base_url}/page/{page}/"
        print(f"Scraping page: {page_url}")
        scrape_indian_express(page_url, collection)


# Main function
if __name__ == "__main__":
    # URL of the Indian Express homepage
    news_url = "https://indianexpress.com/"  # Indian Express main page

    # Connect to MongoDB
    news_collection = connect_to_mongodb()

    # Scrape the news page and store results in MongoDB
    scrape_indian_express(news_url, news_collection)
