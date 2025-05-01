import time
import csv
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from fake_useragent import UserAgent

# ------------------------ Setup Logging ------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AmazonBookScraper")

# ------------------------ Random Delay ------------------------
def random_delay():
    time.sleep(random.uniform(3, 7))

# ------------------------ Configure Chrome Options ------------------------
def create_driver():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(f"user-agent={UserAgent().random}")

    service = Service(executable_path="chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

# ------------------------ Website Navigation ------------------------
def open_website(driver, url):
    try:
        driver.get(url)
        driver.maximize_window()
        logger.info("✅ Website loaded successfully.")
    except WebDriverException as e:
        logger.error(f"❌ Failed to open website: {e}")
        raise

def navigate_to_books_page(driver):
    try:
        books_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/header/div[1]/div[2]/nav/ul/li[3]/a'))
        )
        books_menu.click()
        logger.info("✅ Navigated to Books page.")
    except (TimeoutException, WebDriverException) as e:
        logger.error(f"❌ Failed to navigate to Books page: {e}")
        raise

# ------------------------ Extract Amazon Links ------------------------
def extract_amazon_links(driver):
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'elementor-widget-wrap')]//a"))
        )
        book_links = driver.find_elements(By.XPATH, "//div[contains(@class, 'elementor-widget-wrap')]//a")
        amazon_links = [link.get_attribute("href") for link in book_links if link.get_attribute("href") and "amazon.com" in link.get_attribute("href")]
        logger.info(f"✅ Found {len(amazon_links)} Amazon links.")
        return amazon_links
    except Exception as e:
        logger.error(f"❌ Error extracting Amazon links: {e}")
        raise

# ------------------------ Scrape Amazon Book Data ------------------------
def scrape_amazon_books(driver, amazon_links):
    seen_titles = set()

    with open('amazon_books.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Rating', 'Size', 'Link'])

        for link in amazon_links:
            try:
                driver.get(link)
                random_delay()

                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.ID, 'productTitle'))
                )
                title = driver.find_element(By.ID, 'productTitle').text.strip()

                if title in seen_titles:
                    logger.info(f"⚠️ Skipping duplicate book: {title}")
                    continue
                seen_titles.add(title)

                # Price
                try:
                    price = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div[13]/div[1]/div[2]/div/div/ul/div/div[1]/span/span/a/span[3]/span/span/span').text.strip()
                except NoSuchElementException:                 
                    try:
                        price = driver.find_element(By.ID, 'priceblock_dealprice').text.strip()
                    except NoSuchElementException:
                        try:
                            price = driver.find_element(By.CSS_SELECTOR, "span.a-price span.a-offscreen").text.strip()
                        except NoSuchElementException:
                            price = "N/A"

                # Rating
                try:
                    rating = driver.find_element(By.XPATH, '//span[@data-asin-feature="acr-average-star-rating"]/span').text.strip()
                except NoSuchElementException:
                    try:
                        rating = driver.find_element(By.ID, 'acrPopover').get_attribute('title')
                    except NoSuchElementException:
                        rating = "N/A"

                # Size
                try:
                    size = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div[16]/div[14]/div/div[1]/div/div/div[2]/div/ol/li[2]/div/div[3]/span/a/span').text.strip()
                except NoSuchElementException:
                    try:
                        size = driver.find_element(By.XPATH, '//*[@id="rpi-attribute-book_details-ebook_pages"]/div[3]/span/a/span').text.strip()
                    except NoSuchElementException:
                        size = "N/A"

                logger.info(f"📚 Title: {title}\n💵 Price: {price}\n⭐ Rating: {rating}\n📏 Size: {size}\n🔗 Link: {link}\n{'-'*60}")
                writer.writerow([title, price, rating, size, link])

            except Exception as e:
                logger.error(f"❌ Error scraping {link}: {e}")
                continue

# ------------------------ Main Routine ------------------------
def main():
    driver = create_driver()
    try:
        open_website(driver, "https://www.neuralnine.com/")
        navigate_to_books_page(driver)
        amazon_links = extract_amazon_links(driver)
        scrape_amazon_books(driver, amazon_links)
        logger.info("🎉 Scraping complete. Check 'amazon_books.csv' for results.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
