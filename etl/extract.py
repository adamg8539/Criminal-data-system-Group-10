import pandas as pd
from pathlib import Path
import sys
import traceback

RAW_FILE = Path("data/raw/RCI_offencebymonth.xlsm")


def extract_data(file_path: Path = RAW_FILE) -> pd.DataFrame:
    """ Read the raw Excel dataset."""

    file_path = Path(file_path)

    if not file_path.exists() or file_path.stat().st_size == 0:
        raise FileNotFoundError(
            f"No readable raw data files found in {file_path.parent}"
        )

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
        
    print(f"[etl.extract] cwd: {Path.cwd()}")
    print(f"[etl.extract] attempting to read: {file_path} -> resolved: {file_path.resolve()}")

    candidates_tried = []

    def list_candidates(directory: Path):
        # Preferred extensions in order
        exts = ["*.xlsm", "*.xlsx", "*.xlsb", "*.xls", "*.csv"]
        seen = []
        for pat in exts:
            for p in sorted(directory.glob(pat)):
                if p not in seen:
                    seen.append(p)
        return seen

    if not file_path.exists() or file_path.stat().st_size == 0:
        # If original missing/empty, try to find another candidate in the folder
        print(f"[etl.extract] Primary file missing or empty: {file_path.resolve()}")
        candidates = list_candidates(file_path.parent)
        # Ensure primary path is attempted first if it exists and non-empty
        if file_path.exists() and file_path.stat().st_size > 0:
            candidates = [file_path] + [p for p in candidates if p != file_path]
        if not candidates:
            print("[etl.extract] No candidate files found in data/raw. Listing directory:")
            for p in file_path.parent.iterdir():
                try:
                    print(f"  {p.name:40} {p.stat().st_size:10d} bytes")
                except OSError:
                    print(f"  {p.name:40} <could not stat>")
            raise FileNotFoundError(f"No readable raw data files found in {file_path.parent}")
    else:
        candidates = [file_path]

    last_exc = None
    for cand in candidates:
        candidates_tried.append(cand)
        try:
            print(f"[etl.extract] attempting to read candidate: {cand} (size={cand.stat().st_size} bytes)")
            if cand.suffix.lower() == ".csv":
                df = pd.read_csv(cand)
            else:
                # Let pandas choose engine where possible; explicit engines can be tried in fallback
                df = pd.read_excel(cand)
            print(f"[etl.extract] successfully read {cand} with shape {getattr(df, 'shape', None)}")
            return df
        except Exception:
            print(f"[etl.extract] Failed to read {cand}. Traceback (most recent call last):", file=sys.stderr)
            traceback.print_exc()
            last_exc = sys.exc_info()
            # continue to next candidate

    # If we get here, no candidate worked
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
