"""Milestone 1: Read-only audit of the 2022 STATS19 collision dataset."""

from pathlib import Path
import hashlib
import pandas as pd

DATA_FILE = Path(
    "data/raw/dft-road-casualty-statistics-collision-2022.csv"
)

REPORT_FILE = Path("docs/audit_output_collision_2022.txt")


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE.resolve()}"
        )

    lines = []

    def report(*items):
        message = " ".join(str(item) for item in items)
        print(message)
        lines.append(message)

    # Verify file metadata.
    file_size = DATA_FILE.stat().st_size
    sha256 = hashlib.sha256()

    with DATA_FILE.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    # Read the original CSV without modifying it.
    df = pd.read_csv(DATA_FILE, low_memory=False)

    report("STATS19 COLLISION DATASET — 2022 AUDIT")
    report("=" * 60)
    report("File:", DATA_FILE)
    report("File size in bytes:", file_size)
    report("SHA-256:", sha256.hexdigest())
    report("Rows:", df.shape[0])
    report("Columns:", df.shape[1])
    report()

    report("COLUMN NAMES")
    report("-" * 60)

    for column in df.columns:
        report(column)

    report()
    report("DATA TYPES")
    report("-" * 60)
    report(df.dtypes.to_string())

    report()
    report("MISSING VALUES")
    report("-" * 60)
    report(df.isna().sum().to_string())

    report()
    report("EXACT DUPLICATE ROWS")
    report("-" * 60)
    report(df.duplicated().sum())

    report()
    report("DUPLICATE COLLISION INDEX VALUES")
    report("-" * 60)

    if "collision_index" in df.columns:
        report(df["collision_index"].duplicated().sum())

    report()
    report("COLLISION SEVERITY COUNTS")
    report("-" * 60)

    if "collision_severity" in df.columns:
        report(
            df["collision_severity"]
            .value_counts(dropna=False)
            .sort_index()
            .to_string()
        )

    report()
    report("COLLISION YEAR COUNTS")
    report("-" * 60)

    if "collision_year" in df.columns:
        report(
            df["collision_year"]
            .value_counts(dropna=False)
            .sort_index()
            .to_string()
        )

    report()
    report("DATE RANGE")
    report("-" * 60)

    if "date" in df.columns:
        dates = pd.to_datetime(
            df["date"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        report("Earliest date:", dates.min())
        report("Latest date:", dates.max())
        report("Unparsed dates:", dates.isna().sum())

    report()
    report("COORDINATE QUALITY")
    report("-" * 60)

    for column in ["longitude", "latitude",
                   "location_easting_osgr",
                   "location_northing_osgr"]:

        if column in df.columns:
            report(f"\n{column}")
            report("Missing:", df[column].isna().sum())
            report("Minimum:", df[column].min())
            report("Maximum:", df[column].max())
            report("Zero values:", (df[column] == 0).sum())
            report("Values equal to -1:", (df[column] == -1).sum())

    report()
    report("LOW-CARDINALITY COLUMN COUNTS")
    report("-" * 60)

    for column in df.columns:
        if df[column].nunique(dropna=False) <= 15:
            report(f"\n{column}")
            report(
                df[column]
                .value_counts(dropna=False)
                .to_string()
            )

    report()
    report("AUDIT COMPLETE")
    report("No source data was modified.")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nAudit report saved to: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()