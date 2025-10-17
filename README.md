# NYC 311 Service Requests Database Automation

A full-stack data pipeline project that automates the ingestion, storage, and visualization of NYC 311 service request data.

## 📊 Dataset Information

**Production Data**:
- Source: NYC Open Data - 311 Service Requests
- Time Period: January 2025
- File: `data/data_311_Jan_2025.csv`
- Records: ~337,000+ complaints
- Size: ~100 MB

**Test Data (CI/CD)**:
- File: `tests/fixtures/311_sample.csv`
- Records: 20 representative samples
- Coverage: All 5 boroughs, multiple agencies, various complaint types
- Purpose: Automated testing in GitHub Actions

## 🎯 Project Overview

This project demonstrates:
- **ETL Pipeline**: Automated data extraction from CSV files with data cleaning and transformation
- **Database Management**: MySQL with optimized indexes for query performance
- **Web Application**: Flask-based interface for searching and analyzing complaints
- **Automated Testing**: Comprehensive Selenium test suite
- **CI/CD**: GitHub Actions pipeline for continuous integration

## 📋 Features

- ✅ Chunked CSV processing for large datasets
- ✅ Data validation and cleaning (handling missing boroughs, invalid dates, NaN values)
- ✅ Idempotent ETL (safe to re-run)
- ✅ Indexed database queries for fast filtering
- ✅ Search by date range, borough, and complaint type
- ✅ Paginated results (50 per page)
- ✅ Aggregate statistics dashboard
- ✅ Automated browser testing
- ✅ Dockerized deployment

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd DatabaseAutomation-GitRepo
```

2. Start the services:
```bash
docker-compose up -d
```

3. Wait for MySQL to initialize (~15 seconds), then run the ETL:
```bash
python etl/etl.py
```

4. Access the web application:
```
http://localhost:5000
```

## 📁 Project Structure

```
.
├── app/
│   ├── main.py              # Flask application
│   └── templates/
│       ├── index.html       # Search page
│       └── aggregate.html   # Statistics page
├── db/
│   └── schema.sql           # Database schema with indexes
├── etl/
│   └── etl.py              # ETL script
├── tests/
│   ├── selenium_test.py    # Automated tests
│   └── fixtures/
│       └── 311_sample.csv  # Test data
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── data/                   # CSV data files (gitignored)
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Flask app container
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🗄️ Database Schema

**Table: `service_requests`**
- `unique_key` (BIGINT, PRIMARY KEY)
- `created_date` (DATETIME, INDEXED)
- `closed_date` (DATETIME)
- `agency` (VARCHAR, INDEXED)
- `complaint_type` (VARCHAR)
- `descriptor` (VARCHAR)
- `borough` (VARCHAR, INDEXED)
- `latitude` (DECIMAL)
- `longitude` (DECIMAL)

**Indexes:**
- `idx_created_date` - Date range queries
- `idx_borough` - Location filtering
- `idx_agency` - Agency filtering
- `idx_date_borough` - Combined date + location

## 🔧 ETL Process

1. **Extract**: Reads CSV in 10,000-row chunks
2. **Transform**:
   - Missing boroughs → "UNKNOWN"
   - Invalid dates → NULL
   - NaN values → NULL
3. **Load**: Uses `REPLACE INTO` for idempotency

**Run ETL:**
```bash
python etl/etl.py
```

## 🌐 Web Application

**Search Page** (`/`)
- Filter by date range, borough, complaint type
- Paginated results
- Navigate between pages

**Aggregate Page** (`/aggregate`)
- Overall statistics
- Complaints per borough
- Top 10 complaint types
- Closure rates

## 🧪 Testing

**Run all tests:**
```bash
pytest tests/selenium_test.py -v
```

**Test Coverage:**
- ✅ Home page loads
- ✅ Search returns results (positive test)
- ✅ Borough filter works
- ✅ Invalid filters return 0 results (negative test)
- ✅ Aggregate page loads
- ✅ Navigation between pages

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Sets up MySQL database
2. Loads schema and indexes
3. Runs ETL on fixture data
4. Starts Flask application
5. Executes Selenium tests in headless Chrome

**Workflow file:** `.github/workflows/ci.yml`

## 🛠️ Technologies Used

- **Backend**: Python 3.11, Flask, PyMySQL
- **Database**: MySQL 8.0
- **Data Processing**: Pandas, NumPy
- **Testing**: Pytest, Selenium WebDriver
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Frontend**: HTML5, CSS3, Jinja2 templates

## 📊 Sample Queries

```sql
-- Complaints in January 2025
SELECT * FROM service_requests
WHERE created_date >= '2025-01-01' AND created_date < '2025-02-01';

-- Brooklyn complaints
SELECT * FROM service_requests WHERE borough = 'BROOKLYN';

-- Top complaint types
SELECT complaint_type, COUNT(*) as count
FROM service_requests
GROUP BY complaint_type
ORDER BY count DESC
LIMIT 10;
```

## 📝 Environment Variables

```bash
DB_HOST=localhost        # Database host
DB_PORT=4408            # External MySQL port
DB_USER=root            # Database user
DB_PASSWORD=rootpass    # Database password
DB_NAME=nyc311         # Database name
```

## 🐳 Docker Services

**MySQL** (`mysql_db_database_automation_assignment3`)
- Port: 4408:3306
- Auto-initializes schema from `db/schema.sql`

**Flask App** (`app_database_automation_assignment3`)
- Port: 5000:5000
- Hot-reload enabled with volume mount

## 📈 Performance

- **ETL Speed**: ~1000-2000 rows/second (varies by system)
- **Query Performance**: All filtered queries use indexes (verified with EXPLAIN)
- **Pagination**: Efficient with LIMIT/OFFSET

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/selenium_test.py -v`
5. Submit a pull request

## 📄 License

This project is for educational purposes as part of a Database Automation course assignment.

## 👤 Author

Student Assignment - Conestoga College

## 🙏 Acknowledgments

- NYC Open Data for the 311 Service Requests dataset
- Conestoga College for the project requirements
- Flask and Selenium communities for excellent documentation
