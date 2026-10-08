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

## Dashboard

After producing `data/processed/crime_long_format.csv`, run:

```powershell
python -m streamlit run app\app.py
```
