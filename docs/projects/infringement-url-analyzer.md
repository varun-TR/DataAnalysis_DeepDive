<div align="center">

# Infringement URL Analyzer

### High-Performance Cybersecurity Data Pipeline

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Parallel Processing](https://img.shields.io/badge/Parallel-Processing-orange?style=for-the-badge)](https://docs.python.org/3/library/concurrent.futures.html)
[![R](https://img.shields.io/badge/R-276DC3?style=for-the-badge&logo=r&logoColor=white)](https://r-project.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)

</div>

---

## Executive Summary

Built a **high-performance data pipeline** to identify and analyze potentially infringing URLs from complex nested data structures. The solution utilizes **multi-core parallel processing** to efficiently handle large-scale data extraction, domain resolution, and IP identification for cybersecurity analysis.

---

## Technical Highlights

| Feature | Implementation |
|---------|----------------|
| **Data Processing** | Nested JSON flattening |
| **Parallelization** | ThreadPoolExecutor (4+ cores) |
| **Network Analysis** | Domain & IP resolution |
| **Output** | Structured CSV reports |
| **Alternative** | R implementation included |

---

## Problem Statement

Online infringement and piracy present significant challenges:
- Complex nested data structures hide malicious URLs
- Manual analysis is time-consuming and error-prone
- Scale of data requires automated processing
- Need to identify domains and IPs for enforcement

---

## Solution Architecture

### Data Pipeline

```
Raw JSON Data (Nested Structure)
            │
            ▼
   ┌─────────────────────┐
   │  Data Flattening    │
   │  (json_normalize)   │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │   URL Extraction    │
   │   (urlparse)        │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Parallel DNS       │
   │  Resolution         │
   │  (ThreadPoolExecutor)│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  IP Identification  │
   │  (socket)           │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Analysis &         │
   │  Visualization      │
   └──────────┬──────────┘
              │
              ▼
      CSV/Excel Reports
```

---

## Core Features

### 1. Data Flattening
Converts deeply nested JSON structures into tabular format for analysis.

```python
from pandas import json_normalize

# Flatten nested JSON
flattened_df = json_normalize(
    data,
    record_path=['items'],
    meta=['id', 'timestamp'],
    errors='ignore'
)
```

### 2. URL Extraction
Parses and extracts URLs from flattened data using robust parsing.

```python
from urllib.parse import urlparse

def extract_url_components(url):
    parsed = urlparse(url)
    return {
        'scheme': parsed.scheme,
        'domain': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params
    }
```

### 3. Parallel Domain Resolution
Multi-threaded DNS resolution for high-throughput processing.

```python
from concurrent.futures import ThreadPoolExecutor
import socket

def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return {'domain': domain, 'ip': ip, 'status': 'resolved'}
    except socket.gaierror:
        return {'domain': domain, 'ip': None, 'status': 'failed'}

# Parallel execution
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(resolve_domain, domains))
```

### 4. IP Analysis
Identifies IP addresses associated with infringing content hosts.

```python
def analyze_ip_frequency(resolved_data):
    ip_counts = resolved_data['ip'].value_counts()
    return ip_counts.head(20)  # Top offending IPs
```

---

## Analysis Outputs

### Distribution Analysis
| Analysis | Description |
|----------|-------------|
| **Domain Distribution** | Frequency of infringing domains |
| **Top URLs** | Most frequently accessed malicious URLs |
| **IP Frequency** | Concentration of content on specific IPs |
| **Content Types** | Categories of pirated content |

### Key Findings

- **Google Drive Links:** Significant presence in infringement data
- **IP Concentration:** Multiple domains sharing same infrastructure
- **Daily Trends:** Patterns in malicious URL creation
- **Missing Data:** Analysis of incomplete records

---

## Performance Optimization

### Parallel Processing Configuration
```python
import multiprocessing

# Configurable CPU cores
CPU_COUNT = multiprocessing.cpu_count()
WORKER_THREADS = min(CPU_COUNT, 4)  # Default 4, configurable

# Batch processing for large datasets
BATCH_SIZE = 1000

def process_in_batches(data, batch_size=BATCH_SIZE):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]
```

### Memory Management
```python
# Chunked reading for large files
def read_large_json(filepath, chunk_size=10000):
    with open(filepath, 'r') as f:
        for chunk in pd.read_json(f, lines=True, chunksize=chunk_size):
            yield chunk
```

---

## Project Structure

```
infringement-url-analyzer/
├── README.md
├── LICENSE (MIT)
├── data/
│   ├── response.json          # Input data
│   └── outputs/
│       ├── extracted_urls.csv
│       ├── resolved_domains.csv
│       └── analysis_report.csv
├── notebooks/
│   └── infringement_analysis.ipynb
├── src/
│   ├── python/
│   │   ├── flatten_json.py
│   │   ├── extract_urls.py
│   │   ├── resolve_domains.py
│   │   └── analyze_results.py
│   └── r/
│       └── analysis.R         # R alternative
└── requirements.txt
```

---

## Installation & Usage

### Prerequisites
```bash
pip install pandas numpy tqdm requests
```

### Run Analysis
```bash
# Clone repository
git clone https://github.com/varun-TR/infringement-url-analyzer.git
cd infringement-url-analyzer

# Run main analysis
python src/python/main.py --input data/response.json --output data/outputs/

# Or run Jupyter notebook
jupyter notebook notebooks/infringement_analysis.ipynb
```

### Configuration
```python
# config.py
CONFIG = {
    'max_workers': 4,           # Parallel threads
    'batch_size': 1000,         # Processing batch size
    'timeout': 5,               # DNS timeout seconds
    'retry_count': 3,           # Retry attempts
    'output_format': 'csv'      # csv or excel
}
```

---

## Skills Demonstrated

- **Python Programming:** Advanced data processing
- **Parallel Processing:** Multi-threaded execution
- **Network Analysis:** DNS resolution, IP identification
- **JSON Processing:** Complex nested structure handling
- **Cybersecurity:** Infringement detection, threat analysis
- **Performance Optimization:** Efficient large-scale data handling
- **Data Visualization:** Trend and pattern analysis

---

## Use Cases

This tool can be applied to:
- **Brand Protection:** Identify counterfeit product listings
- **Copyright Enforcement:** Track pirated content distribution
- **Threat Intelligence:** Map malicious infrastructure
- **Security Research:** Analyze infringement patterns
- **Legal Support:** Generate evidence reports

---

## R Alternative

For R users, an alternative implementation is provided:
```r
library(jsonlite)
library(dplyr)
library(parallel)

# Load and flatten JSON
data <- fromJSON("response.json", flatten = TRUE)

# Parallel domain resolution
cl <- makeCluster(detectCores() - 1)
results <- parLapply(cl, domains, resolve_domain)
stopCluster(cl)
```

---

## License

MIT License - See LICENSE file for details.

---

<div align="center">

**Part of [Data Analysis Portfolio](../README.md)**

</div>
