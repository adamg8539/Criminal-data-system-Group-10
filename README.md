# NSW Criminal Data System

## Dataset

The ETL uses BOCSAR's **Recorded Criminal Incidents by month - by LGA**
workbook. The Selenium fetcher discovers the current download link on the
official dataset page, validates the workbook, and only then replaces the
existing raw file.

```powershell
python -m etl.fetch
```

The resulting file is saved to:

```text
data/raw/RCI_offencebymonth.xlsm
```

To watch Selenium run in Chrome:

```powershell
python -m etl.fetch --show-browser
```

Source: https://bocsar.nsw.gov.au/statistics-dashboards/open-datasets/criminal-offences-data.html

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create the permanent tables in the PostgreSQL database configured in `.env`:

```powershell
python scripts\setup_db.py
```

This is a one-time initialization step. It does not drop existing tables.

## Dashboard

After configuring `.env`, creating the database schema, and loading the data, run:

```powershell
python -m streamlit run app\app.py
```

The dashboard reads its data from the configured PostgreSQL database.
