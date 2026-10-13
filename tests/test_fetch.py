import zipfile
from pathlib import Path

import pytest

from etl.fetch import MINIMUM_WORKBOOK_BYTES, validate_workbook


def _write_workbook_container(path: Path, *, include_workbook: bool = True) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        if include_workbook:
            archive.writestr("xl/workbook.xml", "<workbook />")
        archive.writestr(
            "padding.bin",
            b"0" * (MINIMUM_WORKBOOK_BYTES + 1),
        )


def test_validate_workbook_accepts_excel_container(tmp_path: Path) -> None:
    workbook = tmp_path / "dataset.xlsm"
    _write_workbook_container(workbook)

    validate_workbook(workbook)


def test_validate_workbook_rejects_non_excel_payload(tmp_path: Path) -> None:
    payload = tmp_path / "dataset.xlsm"
    payload.write_bytes(b"not an Excel workbook" * 10_000)

    with pytest.raises(ValueError, match="not a valid"):
        validate_workbook(payload)


def test_validate_workbook_requires_workbook_manifest(tmp_path: Path) -> None:
    workbook = tmp_path / "dataset.xlsm"
    _write_workbook_container(workbook, include_workbook=False)

    with pytest.raises(ValueError, match="does not contain"):
        validate_workbook(workbook)
