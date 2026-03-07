import csv
from pathlib import Path
from typing import Iterable, Sequence

from .models import ChromosomeRecord
from .utils import DEFAULT_COLUMNS, filter_columns


def export_records(
    records: Iterable[ChromosomeRecord],
    output_path: str | Path,
    fmt: str = "csv",
    append: bool = False,
    exclude_columns: Sequence[str] | None = None,
) -> Path:
    rows = [filter_columns(record.to_dict(), exclude_columns) for record in records]
    if not rows:
        return Path(output_path)

    delimiter = "," if fmt.lower() == "csv" else "	"
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [column for column in DEFAULT_COLUMNS if column in rows[0]]
    mode = "a" if append else "w"
    write_header = not append or not path.exists() or path.stat().st_size == 0

    with path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    return path
