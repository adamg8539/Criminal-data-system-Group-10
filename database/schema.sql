CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE UNIQUE,
    year INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT
);

CREATE TABLE dim_location (
    location_id SERIAL PRIMARY KEY,
    lga VARCHAR(100) UNIQUE,
    state VARCHAR(50)
);

CREATE TABLE dim_offence (
    offence_id SERIAL PRIMARY KEY,
    offence_category VARCHAR(100),
    offence_subcategory VARCHAR(150),
    UNIQUE (offence_category, offence_subcategory)
);

CREATE TABLE fact_crime (
    crime_id SERIAL PRIMARY KEY,
    date_id INT REFERENCES dim_date(date_id),
    location_id INT REFERENCES dim_location(location_id),
    offence_id INT REFERENCES dim_offence(offence_id),
    incident_count INT
);