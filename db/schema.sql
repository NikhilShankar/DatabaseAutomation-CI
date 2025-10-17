CREATE DATABASE IF NOT EXISTS nyc311;
USE nyc311;

CREATE TABLE IF NOT EXISTS service_requests (
  unique_key BIGINT PRIMARY KEY,
  created_date DATETIME NOT NULL,
  closed_date DATETIME NULL,
  agency VARCHAR(16),
  complaint_type VARCHAR(128),
  descriptor VARCHAR(255),
  borough VARCHAR(32),
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6)
);

-- Index 1: Speed up date range queries (most common filter)
CREATE INDEX idx_created_date ON service_requests(created_date);

-- Index 2: Speed up borough filtering (location-based queries)
CREATE INDEX idx_borough ON service_requests(borough);

-- Index 3: Speed up agency filtering (department-specific reports)
CREATE INDEX idx_agency ON service_requests(agency);

-- Index 4: Composite index for common combined filters (date + borough)
CREATE INDEX idx_date_borough ON service_requests(created_date, borough);
