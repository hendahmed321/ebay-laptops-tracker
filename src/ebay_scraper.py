# Web Scraping eBay Laptops
#### This project scrapes laptop data from eBay, processes it, and stores it in MongoDB for analysis.
## Importing Libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import re
## Setup Selenium WebDriver 
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver
## Data Cleaning and Preprocessing
### Price Cleaning
def clean_price(price_text): 
    # Find numbers in price text (handle commas and decimals)
    match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
    if match:
        return float(match.group())
    return None
### Get info from title
def extract_brand(title):
    brands = ['lenovo', 'dell', 'hp', 'apple', 'asus', 'msi', 'acer', 
              'samsung', 'microsoft', 'lg', 'toshiba', 'sony', 'razor']
    
    title_lower = title.lower()
    for brand in brands:
        if brand in title_lower:
            return brand.title() 
    return None
### Extract Technical Specifications
def extract_specs(title):
    specs = {}
    
    if not title:
        return specs
    
    # RAM 
    ram_match = re.search(r'(\d+)\s*GB?\s*(RAM|Ram|Memory|DDR)', title, re.IGNORECASE)
    if ram_match:
        specs['ram'] = f"{ram_match.group(1)}GB"
    
    # Storage 
    storage_match = re.search(r'(\d+TB|\d+GB)\s*(SSD|HDD|NVMe|Storage)', title, re.IGNORECASE)
    if storage_match:
        specs['storage'] = storage_match.group(1)
    
    # Processor 
    if 'ryzen' in title.lower():
        specs['processor'] = 'AMD Ryzen'
    elif 'intel' in title.lower() or any(cpu in title for cpu in ['i3', 'i5', 'i7', 'i9']):
        specs['processor'] = 'Intel'
    elif 'm1' in title or 'm2' in title or 'm3' in title:
        specs['processor'] = 'Apple Silicon'
    
    # Screen 
    screen_match = re.search(r'(\d+\.?\d*)"', title)
    if screen_match:
        specs['screen_size'] = f"{screen_match.group(1)}\""
    
    # Graphics
    gpu_match = re.search(r'(RTX\s*\d+|GTX\s*\d+|Radeon\s*\w+)', title, re.IGNORECASE)
    if gpu_match:
        specs['graphics'] = gpu_match.group(1)
    
    return specs
### Splitting condition and brand
def clean_condition_brand(text):
    # Remove duplicate newlines + extra spaces
    text = " ".join(text.split())

    # Split by "·"
    if "·" in text:
        parts = [p.strip() for p in text.split("·")]
        if len(parts) == 2:
            condition = parts[0]
            brand = parts[1]
            return condition, brand
    
    return text, None

## Scrapping 
def scrape_ebay_laptops(pages_to_scrape=3):
    driver = setup_driver()
    all_products = []
    
    try:
        for page in range(1, pages_to_scrape + 1):
            print(f"Scraping page {page}...")

            url = f"https://www.ebay.com/b/Laptops-Netbooks/175672/bn_1648276?_sop=12&mag=1&rt=nc&_pgn={page}"
            driver.get(url)

            time.sleep(5)  # allow content to load

            product_containers = driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'card__body')]"
            )

            print(f"Found {len(product_containers)} products on page {page}")

            for container in product_containers:
                try:
                    product_data = {}

                    # Title
                    try:
                        title_element = container.find_element(
                            By.XPATH, 
                            ".//h3[contains(@class, 'title')]"
                        )
                        title = title_element.text.strip()
                        if not title or "Shop on eBay" in title:
                            continue
                        product_data["title"] = title

                        # Extract specs from title
                        specs = extract_specs(title)
                        product_data.update(specs)

                    except:
                        continue

                    # Price
                    try:
                        price_element = container.find_element(
                            By.XPATH, 
                            ".//span[contains(@class, 'price')]"
                        )
                        product_data["price"] = clean_price(price_element.text)
                    except:
                        continue

                    # Characteristics
                    try: 
                        Characteristics = container.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'listingCondition')]"
                        )
                        raw_text = Characteristics.text.strip()
                        condition, brand = clean_condition_brand(raw_text)
                        product_data["condition"] = condition
                        product_data["brand"] = brand
                    except:
                        continue

                    # Quantity lefy
                    try: 
                        quantity = container.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'negative')]"
                        ).text
                        product_data["Quantity"] = quantity
                    except:
                        continue

                    # Image
                    try:
                        img = container.find_element(By.XPATH, ".//img").get_attribute("src")
                        if "gif" in img:  
                            img = container.find_element(By.XPATH, ".//img").get_attribute("data-src")
                        product_data["img"] = img
                    except:
                        continue


                    all_products.append(product_data)

                except:
                    continue

            time.sleep(1)

        return all_products

    finally:
        driver.quit()
# Saving the JSON file into mongoDB 
from pymongo import MongoClient
import json
from datetime import datetime
class MongoDBHandler:
    def __init__(self):
        self.connection_string = "mongodb+srv://hndahmdharwn_db_user:Hend123@cluster0.dnewrag.mongodb.net/"
        self.client = None
        self.db = None
        self.collection = None
    
    # Conncet to MongoDB Atlas
    def connect(self):
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.client.server_info()
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False
    
    # Setting the database and conncetion
    def setup_database(self, db_name="Ebay_Project", collection_name="laptops"):
        if not self.client:
            return False
        
        try:
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            print(f"Using database: {db_name}")
            print(f"Using collection: {collection_name}")
            return True
        except Exception as e:
            print(f"Database setup error: {e}")
            return False
    
    def delete_old_data(self):
        if self.collection is None:  
            return 0
        
        try:
            result = self.collection.delete_many({})
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting old data: {e}")
            return 0
    
    # Saving the laptops to MongoDB (with delete old option)
    def save_products_fresh(self, products, delete_old=True):
        if not products:
            print("No products to save")
            return 0
    
        if not self.client:
            if not self.connect():
                return 0
            
        if self.collection is None:  
            if not self.setup_database():
                return 0
           
        try:
            # Delete old data first
            if delete_old:
                self.delete_old_data()
            
            # Add timestamp
            for product in products:
                product["stored_at"] = datetime.now()
            
            # Saving Data
            result = self.collection.insert_many(products)
            saved_count = len(result.inserted_ids)
            print(f"Saved {saved_count} new products to MongoDB Atlas!")
            
            # Show total in DB
            total = self.collection.count_documents({})
            print(f"Total in database: {total}")
            
            return saved_count
            
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return 0
        
    # Additional step
    def save_backup_json(self, products, filename=None):
        if not products:
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebay_laptops_backup_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, default=str)
            
            print(f"JSON backup saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return None
# RUN EVERYTHING (Scrapping + Storing)
## Scrapping
if __name__ == "__main__":
    products = scrape_ebay_laptops()
    for i, product in enumerate(products[:5]):  
        print(f"\nProduct {i+1}:")
        for key, value in product.items():
            print(f"  {key}: {value}")

    mongodb = MongoDBHandler()
    saved_count = mongodb.save_products_fresh(products, delete_old=True)
    backup_file = mongodb.save_backup_json(products)