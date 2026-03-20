CREATE VIEW vw_crimes_by_year AS
SELECT d.year, SUM(f.incident_count) AS total_incidents
FROM fact_crime f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year
ORDER BY d.year;

CREATE VIEW vw_crimes_by_location AS
SELECT l.lga, SUM(f.incident_count) AS total_incidents
FROM fact_crime f
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY l.lga
ORDER BY total_incidents DESC;

CREATE VIEW vw_crimes_by_offence AS
SELECT o.offence_category, SUM(f.incident_count) AS total_incidents
FROM fact_crime f
JOIN dim_offence o ON f.offence_id = o.offence_id
GROUP BY o.offence_category
ORDER BY total_incidents DESC;