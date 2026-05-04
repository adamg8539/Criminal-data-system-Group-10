CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1995 AND 2030),
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    quarter VARCHAR(2) NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL
);

CREATE TABLE dim_location (
    location_id SERIAL PRIMARY KEY,
    lga VARCHAR(100) UNIQUE NOT NULL,
    region VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL DEFAULT 'NSW'
);

CREATE TABLE dim_offence (
    offence_id SERIAL PRIMARY KEY,
    offence_category VARCHAR(100) NOT NULL,
    offence_subcategory VARCHAR(150) NOT NULL,
    offence_group VARCHAR(50) NOT NULL,
    UNIQUE (offence_category, offence_subcategory)
);

CREATE TABLE fact_crime (
    crime_id SERIAL PRIMARY KEY,
    date_id INT NOT NULL REFERENCES dim_date(date_id),
    location_id INT NOT NULL REFERENCES dim_location(location_id),
    offence_id INT NOT NULL REFERENCES dim_offence(offence_id),
    incident_count INT NOT NULL CHECK (incident_count >= 0),
    UNIQUE (date_id, location_id, offence_id)
);

-- Indexes on FK columns for join performance (NFR-09)
CREATE INDEX idx_fact_crime_date_id     ON fact_crime(date_id);
CREATE INDEX idx_fact_crime_location_id ON fact_crime(location_id);
CREATE INDEX idx_fact_crime_offence_id  ON fact_crime(offence_id);

CREATE TABLE etl_load_history (
    load_id SERIAL PRIMARY KEY,
    run_at TIMESTAMP NOT NULL DEFAULT NOW(),
    rows_extracted INT,
    rows_after_validation INT,
    rows_transformed INT,
    rows_loaded INT,
    incremental_from DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed')),
    error_message TEXT
);
