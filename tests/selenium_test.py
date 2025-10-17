import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def driver():
    """Setup and teardown for Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

class TestSearchPage:
    """Tests for the main search page"""

    def test_home_page_loads(self, driver):
        """Test that the home page loads successfully"""
        driver.get(BASE_URL)
        assert "NYC 311 Service Requests" in driver.title

        # Check that key elements exist
        assert driver.find_element(By.TAG_NAME, "h1")
        assert driver.find_element(By.CSS_SELECTOR, "form.search-form")
        assert driver.find_element(By.NAME, "date_from")
        assert driver.find_element(By.NAME, "date_to")
        assert driver.find_element(By.NAME, "borough")
        assert driver.find_element(By.NAME, "complaint_type")

    def test_positive_search_returns_results(self, driver):
        """Positive test: Search form returns results"""
        driver.get(BASE_URL)

        # Fill in search form
        date_from = driver.find_element(By.NAME, "date_from")
        date_from.send_keys("2025-01-01")

        date_to = driver.find_element(By.NAME, "date_to")
        date_to.send_keys("2025-01-31")

        # Submit form
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Wait for results to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Verify results are displayed
        stats = driver.find_element(By.CLASS_NAME, "stats").text
        assert "Total Records Found:" in stats

        # Check that table exists and has rows
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        assert len(rows) > 1  # Header + at least 1 data row

    def test_borough_filter(self, driver):
        """Positive test: Filter by borough"""
        driver.get(BASE_URL)

        # Select a borough from dropdown
        borough_select = Select(driver.find_element(By.NAME, "borough"))
        # Get first non-"All" option
        options = borough_select.options
        if len(options) > 1:
            borough_select.select_by_index(1)  # Select first borough

            # Submit form
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_btn.click()

            # Verify URL contains borough parameter
            assert "borough=" in driver.current_url

    def test_negative_invalid_date_range(self, driver):
        """Negative test: Invalid date range returns 0 or fewer results"""
        driver.get(BASE_URL)

        # Enter future date range (should return 0 results for January 2025 data)
        date_from = driver.find_element(By.NAME, "date_from")
        date_from.send_keys("2026-12-01")

        date_to = driver.find_element(By.NAME, "date_to")
        date_to.send_keys("2026-12-31")

        # Submit form
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Wait for page to load
        time.sleep(2)

        # Check that either "No results found" message appears OR total is 0
        page_text = driver.page_source
        stats_text = driver.find_element(By.CLASS_NAME, "stats").text

        assert ("No results found" in page_text or
                "Total Records Found: 0" in stats_text)

    def test_negative_nonexistent_complaint_type(self, driver):
        """Negative test: Searching for non-existent complaint type returns 0 results"""
        driver.get(BASE_URL)

        # Enter a complaint type that doesn't exist
        complaint_type = driver.find_element(By.NAME, "complaint_type")
        complaint_type.send_keys("XYZNONEXISTENT12345")

        # Submit form
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Wait for page to load
        time.sleep(2)

        # Verify no results or zero count
        page_text = driver.page_source
        assert ("No results found" in page_text or
                "Total Records Found: 0" in driver.find_element(By.CLASS_NAME, "stats").text)

    def test_pagination_exists(self, driver):
        """Test that pagination controls appear when there are results"""
        driver.get(BASE_URL)

        # Search with date filter to get results
        date_from = driver.find_element(By.NAME, "date_from")
        date_from.send_keys("2025-01-01")

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Wait for results
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pagination")))

        # Verify pagination element exists
        pagination = driver.find_element(By.CLASS_NAME, "pagination")
        assert pagination is not None
        assert "Page" in pagination.text

class TestAggregatePage:
    """Tests for the aggregate statistics page"""

    def test_aggregate_page_loads(self, driver):
        """Aggregate test: Complaints per Borough page loads"""
        driver.get(f"{BASE_URL}/aggregate")

        # Verify page title
        assert "Aggregate Statistics" in driver.page_source

        # Verify key sections exist
        assert driver.find_element(By.TAG_NAME, "h1")

        # Check for "Overall Statistics" section
        page_text = driver.page_source
        assert "Overall Statistics" in page_text

        # Check for "Complaints by Borough" section
        assert "Complaints by Borough" in page_text

        # Check for "Top 10 Complaint Types" section
        assert "Top 10 Complaint Types" in page_text

    def test_aggregate_stats_cards(self, driver):
        """Test that aggregate statistics cards display data"""
        driver.get(f"{BASE_URL}/aggregate")

        # Wait for stats cards to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "stat-card")))

        # Check that stat cards exist
        stat_cards = driver.find_elements(By.CLASS_NAME, "stat-card")
        assert len(stat_cards) >= 3  # At least Total, Closed, Open

        # Verify each card has a number
        for card in stat_cards:
            card_text = card.text
            assert len(card_text) > 0  # Card has content

    def test_aggregate_borough_table(self, driver):
        """Test that borough statistics table displays"""
        driver.get(f"{BASE_URL}/aggregate")

        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Find all tables on page
        tables = driver.find_elements(By.TAG_NAME, "table")
        assert len(tables) >= 2  # Borough table + Top complaints table

        # Check first table has data
        first_table = tables[0]
        rows = first_table.find_elements(By.TAG_NAME, "tr")
        assert len(rows) > 1  # Header + at least 1 borough row

    def test_aggregate_top_complaints(self, driver):
        """Test that top complaints table displays"""
        driver.get(f"{BASE_URL}/aggregate")

        # Wait for tables to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Find all tables
        tables = driver.find_elements(By.TAG_NAME, "table")

        # Second table should be top complaints
        if len(tables) >= 2:
            top_complaints_table = tables[1]
            rows = top_complaints_table.find_elements(By.TAG_NAME, "tr")
            assert len(rows) > 1  # Header + complaint rows

class TestNavigation:
    """Tests for navigation between pages"""

    def test_nav_links_exist(self, driver):
        """Test that navigation links exist on both pages"""
        # Test from home page
        driver.get(BASE_URL)
        nav = driver.find_element(By.CLASS_NAME, "nav")
        links = nav.find_elements(By.TAG_NAME, "a")
        assert len(links) >= 2  # Search and Aggregate links

    def test_navigate_to_aggregate(self, driver):
        """Test navigation from home to aggregate page"""
        driver.get(BASE_URL)

        # Click aggregate link
        aggregate_link = driver.find_element(By.LINK_TEXT, "Aggregate Stats")
        aggregate_link.click()

        # Verify we're on aggregate page
        assert "/aggregate" in driver.current_url
        assert "Aggregate Statistics" in driver.page_source

    def test_navigate_back_to_search(self, driver):
        """Test navigation from aggregate back to search page"""
        driver.get(f"{BASE_URL}/aggregate")

        # Click search link
        search_link = driver.find_element(By.LINK_TEXT, "Search")
        search_link.click()

        # Verify we're back on search page
        assert driver.current_url == f"{BASE_URL}/" or driver.current_url == BASE_URL
        assert "NYC 311 Service Requests" in driver.page_source

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
