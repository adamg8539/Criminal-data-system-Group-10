"""Download the latest BOCSAR LGA workbook using Selenium."""

from __future__ import annotations

import argparse
import hashlib
import os
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


DATASET_PAGE_URL = (
    "https://bocsar.nsw.gov.au/statistics-dashboards/open-datasets/"
    "criminal-offences-data.html"
)
DOWNLOAD_FILENAME = "RCI_offencebymonth.xlsm"
DEFAULT_DESTINATION = Path("data/raw") / DOWNLOAD_FILENAME
DOWNLOAD_LINK_XPATH = (
    "//a[contains(@href, 'RCI_offencebymonth.xlsm') "
    "or contains(normalize-space(.), 'Recorded Criminal Incidents by month - by LGA')]"
)
MINIMUM_WORKBOOK_BYTES = 100_000


@dataclass(frozen=True)
class DownloadResult:
    destination: Path
    source_url: str
    size_bytes: int
    sha256: str


def _build_driver(download_directory: Path, *, headless: bool) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1200")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": str(download_directory)},
    )
    return driver


def _wait_for_download(download_directory: Path, timeout_seconds: int) -> Path:
    destination = download_directory / DOWNLOAD_FILENAME
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        partial_downloads = list(download_directory.glob("*.crdownload"))
        if destination.is_file() and destination.stat().st_size > 0 and not partial_downloads:
            return destination
        time.sleep(0.25)

    raise TimeoutError(
        f"BOCSAR download did not finish within {timeout_seconds} seconds."
    )


def validate_workbook(path: Path) -> None:
    """Reject error pages, partial files, and non-Excel payloads."""
    if not path.is_file():
        raise ValueError(f"Downloaded file does not exist: {path}")
    if path.stat().st_size < MINIMUM_WORKBOOK_BYTES:
        raise ValueError(
            f"Downloaded file is unexpectedly small ({path.stat().st_size} bytes)."
        )
    if not zipfile.is_zipfile(path):
        raise ValueError("Downloaded payload is not a valid XLSM/XLSX container.")

    with zipfile.ZipFile(path) as workbook:
        members = set(workbook.namelist())
    if "xl/workbook.xml" not in members:
        raise ValueError("Downloaded payload does not contain an Excel workbook.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_dataset(
    destination: Path = DEFAULT_DESTINATION,
    *,
    headless: bool = True,
    timeout_seconds: int = 120,
) -> DownloadResult:
    """Discover, download, validate, and atomically publish the latest workbook."""
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(
        prefix=".bocsar-download-", dir=destination.parent
    ) as temporary_directory:
        download_directory = Path(temporary_directory).resolve()
        driver = _build_driver(download_directory, headless=headless)
        try:
            driver.get(DATASET_PAGE_URL)
            link = WebDriverWait(driver, timeout_seconds).until(
                EC.element_to_be_clickable((By.XPATH, DOWNLOAD_LINK_XPATH))
            )
            source_url = link.get_attribute("href")
            if not source_url:
                raise ValueError("BOCSAR download link did not contain a URL.")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", link
            )
            try:
                link.click()
            except ElementClickInterceptedException:
                # The NSW feedback panel can overlap the link in headless Chrome.
                driver.execute_script("arguments[0].click();", link)
            downloaded_file = _wait_for_download(download_directory, timeout_seconds)
        except TimeoutException as exc:
            raise TimeoutError("Could not find the BOCSAR LGA download link.") from exc
        finally:
            driver.quit()

        validate_workbook(downloaded_file)
        size_bytes = downloaded_file.stat().st_size
        checksum = _sha256(downloaded_file)
        os.replace(downloaded_file, destination)

    return DownloadResult(
        destination=destination,
        source_url=source_url,
        size_bytes=size_bytes,
        sha256=checksum,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download the latest BOCSAR LGA incident workbook."
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help=f"Output path (default: {DEFAULT_DESTINATION})",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Show Chrome while Selenium performs the download.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    result = fetch_dataset(
        args.destination,
        headless=not args.show_browser,
        timeout_seconds=args.timeout,
    )
    print(f"Downloaded from: {result.source_url}")
    print(f"Saved to: {result.destination}")
    print(f"Size: {result.size_bytes:,} bytes")
    print(f"SHA-256: {result.sha256}")


if __name__ == "__main__":
    main()
