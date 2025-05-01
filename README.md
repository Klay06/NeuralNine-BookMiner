# 📚 AmazonBookScraper

**AmazonBookScraper** is a Python-based web scraper designed to extract detailed information about books listed on Amazon, starting from book links collected on the [NeuralNine](https://www.neuralnine.com/) website.

It automates the process of gathering book titles, prices, ratings, and sizes, and saves the results in a structured CSV file for analysis or archiving.

---

## 🚀 Features

- Automatically navigates to NeuralNine's book listing page  
- Extracts all Amazon book links  
- Visits each Amazon product page and scrapes:
  - ✅ Title  
  - ✅ Price (with multiple fallback strategies)  
  - ✅ Average Rating  
  - ✅ File/Print Size  
- Stores results in a `amazon_books.csv` file  
- Simulates human browsing with:
  - ⏱ Random delays  
  - 🕵️‍♂️ Rotating user agents  
- Structured logging for debugging

---

## 🛠 Tech Stack

- Python 3  
- Selenium WebDriver  
- Fake UserAgent  
- CSV (for data storage)  
- Built-in `logging` module

---