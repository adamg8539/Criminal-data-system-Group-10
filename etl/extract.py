import pandas as pd
from pathlib import Path
import sys
import traceback

RAW_FILE = Path("data/raw/RCI_offencebymonth.xlsm")


def extract_data(file_path: Path = RAW_FILE) -> pd.DataFrame:
    """Read the raw Excel dataset, falling back to other candidates in the same folder."""

    file_path = Path(file_path)

    def list_candidates(directory: Path):
        exts = ["*.xlsm", "*.xlsx", "*.xlsb", "*.xls", "*.csv"]
        seen = []
        for pat in exts:
            for p in sorted(directory.glob(pat)):
                if p not in seen:
                    seen.append(p)
        return seen

    if file_path.exists() and file_path.stat().st_size > 0:
        candidates = [file_path]
    else:
        print(f"[etl.extract] Primary file missing or empty: {file_path.resolve()}")
        candidates = list_candidates(file_path.parent)
        if not candidates:
            print("[etl.extract] No candidate files found in data/raw. Listing directory:")
            for p in file_path.parent.iterdir():
                try:
                    print(f"  {p.name:40} {p.stat().st_size:10d} bytes")
                except OSError:
                    print(f"  {p.name:40} <could not stat>")
            raise FileNotFoundError(f"No readable raw data files found in {file_path.parent}")

    last_exc = None
    candidates_tried = []
    for cand in candidates:
        candidates_tried.append(cand)
        try:
            print(f"[etl.extract] attempting to read: {cand.resolve()} (size={cand.stat().st_size} bytes)")
            if cand.suffix.lower() == ".csv":
                df = pd.read_csv(cand)
            else:
                df = pd.read_excel(cand)
            print(f"[etl.extract] successfully read {cand.name} with shape {df.shape}")
            return df
        except Exception:
            print(f"[etl.extract] Failed to read {cand}:", file=sys.stderr)
            traceback.print_exc()
            last_exc = sys.exc_info()

    tried = ", ".join(str(p.name) for p in candidates_tried)
    raise RuntimeError(f"Unable to read any candidate files ({tried}). Last error: {last_exc[1] if last_exc else 'unknown'}")


if __name__ == "__main__":
    try:
        df = extract_data()
        print("\n[etl.extract] Data sample (head):")
        print(df.head())
        print("\n[etl.extract] Columns:")
        print(df.columns.tolist())
    except Exception as e:
        print(f"[etl.extract] Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)
