<div align="center">

# Academic Journal Web Scraper

### Automated Research Data Extraction Pipeline

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)

</div>

---

## Executive Summary

Engineered an **automated web scraping solution** to extract scholarly article metadata from academic journal websites. The tool captures comprehensive research data including titles, abstracts, authors, DOIs, affiliations, and ORCID identifiers, enabling efficient research data management and analysis.

---

## Technical Highlights

| Component | Technology |
|-----------|------------|
| **Automation** | Selenium WebDriver |
| **Browser** | Chrome/Chromedriver |
| **Data Processing** | Pandas |
| **Development** | Jupyter Notebook |
| **Output Formats** | CSV, Excel |

---

## Problem Statement

Researchers and institutions need to:
- Collect metadata from multiple journal articles
- Build research databases for analysis
- Track publication metrics and trends
- Create literature review datasets
- Automate repetitive data collection tasks

---

## Solution Features

### Data Extraction Capabilities

| Field | Description |
|-------|-------------|
| **Title** | Article title |
| **Abstract** | Full article abstract |
| **Authors** | All author names |
| **Affiliations** | Author institutional affiliations |
| **ORCID** | Author ORCID identifiers |
| **DOI** | Digital Object Identifier |
| **Publication Date** | Article publication date |
| **Keywords** | Article keywords/tags |

---

## Architecture

### Scraping Pipeline

```
Target Journal Website
         │
         ▼
┌─────────────────────┐
│  Selenium WebDriver │
│  (Chrome Browser)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Page Navigation    │
│  • Pagination       │
│  • Article links    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Element Location   │
│  • XPath selectors  │
│  • CSS selectors    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Extraction    │
│  • Text content     │
│  • Attributes       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Error Handling     │
│  • Missing fields   │
│  • Timeout recovery │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Storage       │
│  • CSV export       │
│  • Excel export     │
└─────────────────────┘
```

---

## Implementation

### Browser Setup
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize driver
service = Service('/path/to/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Element Location
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for element to load
wait = WebDriverWait(driver, 10)
title_element = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "article-title"))
)

# Extract text
title = title_element.text
```

### Data Extraction Functions
```python
def extract_article_data(driver, article_url):
    """Extract metadata from a single article page."""
    driver.get(article_url)

    data = {
        'title': safe_extract(driver, "//h1[@class='article-title']"),
        'abstract': safe_extract(driver, "//div[@class='abstract']"),
        'authors': safe_extract_list(driver, "//span[@class='author-name']"),
        'affiliations': safe_extract_list(driver, "//span[@class='affiliation']"),
        'doi': safe_extract(driver, "//a[@class='doi-link']", attribute='href'),
        'publication_date': safe_extract(driver, "//span[@class='pub-date']"),
        'orcid': safe_extract_list(driver, "//a[@class='orcid-link']", attribute='href')
    }

    return data

def safe_extract(driver, xpath, attribute=None):
    """Safely extract element with error handling."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        if attribute:
            return element.get_attribute(attribute)
        return element.text
    except:
        return None
```

### Batch Processing
```python
def scrape_journal_articles(base_url, num_pages=10):
    """Scrape articles across multiple pages."""
    all_articles = []

    for page in range(1, num_pages + 1):
        page_url = f"{base_url}?page={page}"
        driver.get(page_url)

        # Get article links
        article_links = driver.find_elements(By.XPATH, "//a[@class='article-link']")
        urls = [link.get_attribute('href') for link in article_links]

        # Extract each article
        for url in urls:
            article_data = extract_article_data(driver, url)
            all_articles.append(article_data)
            time.sleep(1)  # Respectful delay

        print(f"Completed page {page}/{num_pages}")

    return pd.DataFrame(all_articles)
```

---

## Error Handling

### Robust Extraction
```python
def safe_extract_with_retry(driver, xpath, retries=3):
    """Extract with retry logic for reliability."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text
        except TimeoutException:
            if attempt < retries - 1:
                driver.refresh()
                time.sleep(2)
            continue
    return None
```

### Handling Missing Data
```python
def clean_extracted_data(df):
    """Clean and validate extracted data."""
    # Fill missing values
    df['abstract'] = df['abstract'].fillna('Abstract not available')

    # Validate DOIs
    df['valid_doi'] = df['doi'].apply(lambda x: x is not None and 'doi.org' in str(x))

    # Flag incomplete records
    required_fields = ['title', 'authors', 'doi']
    df['complete'] = df[required_fields].notna().all(axis=1)

    return df
```

---

## Output Formats

### CSV Export
```python
# Export to CSV
df.to_csv('output-final.csv', index=False, encoding='utf-8')
```

### Excel Export
```python
# Export to Excel with formatting
with pd.ExcelWriter('output-final.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Articles', index=False)

    # Auto-adjust column widths
    worksheet = writer.sheets['Articles']
    for column in worksheet.columns:
        max_length = max(len(str(cell.value)) for cell in column)
        worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
```

---

## Project Structure

```
Webscrapper_for_journals/
├── README.md
├── LICENSE (MIT)
├── notebooks/
│   └── journal_scraper.ipynb
├── src/
│   ├── scraper.py
│   ├── extractors.py
│   └── utils.py
├── config/
│   └── selectors.yaml
├── output/
│   ├── output-final.csv
│   └── output-final.xlsx
├── requirements.txt
└── chromedriver/
    └── README.md (driver setup instructions)
```

---

## Installation & Setup

### Prerequisites
```bash
# Install Python dependencies
pip install selenium pandas openpyxl webdriver-manager

# Alternative: use requirements.txt
pip install -r requirements.txt
```

### ChromeDriver Setup
```bash
# Option 1: Manual download
# Download from: https://chromedriver.chromium.org/
# Place in chromedriver/ directory

# Option 2: Automatic with webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

### Run Scraper
```bash
# Run Jupyter notebook
jupyter notebook notebooks/journal_scraper.ipynb

# Or run Python script
python src/scraper.py --url "https://journal-website.com/articles" --pages 10
```

---

## Best Practices

### Ethical Scraping
1. **Respect robots.txt:** Check site's scraping policies
2. **Rate Limiting:** Add delays between requests
3. **User Agent:** Identify your scraper appropriately
4. **Data Use:** Comply with terms of service

### Performance Tips
1. **Headless Mode:** Faster execution without GUI
2. **Selective Loading:** Disable images/CSS when not needed
3. **Batch Processing:** Group requests efficiently
4. **Caching:** Store intermediate results

---

## Skills Demonstrated

- **Web Scraping:** Selenium WebDriver automation
- **Browser Automation:** Headless Chrome control
- **Data Extraction:** Complex page parsing
- **Error Handling:** Robust retry mechanisms
- **Python Programming:** OOP, generators, context managers
- **Data Processing:** Pandas data manipulation
- **Research Tools:** Academic data management

---

## Use Cases

- Literature review data collection
- Citation analysis research
- Publication tracking systems
- Research trend analysis
- Academic portfolio management
- Institutional research databases

---

## License

MIT License - See LICENSE file for details.

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
