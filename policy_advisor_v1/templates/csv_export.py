"""CSV exporter for parliamentary_classic / policy_advisor_v1.

Writes the lever x actor x horizon matrix (and any other tabular slice) to
a UTF-8 CSV with a BOM, so Excel on Windows opens it with the correct
encoding without prompting. Idempotent: same input dict order => identical
bytes on disk.

Usage:
    python csv_export.py --rows rows.json --out matrix.csv

Or programmatically:
    from csv_export import write_csv
    write_csv(rows, fieldnames, Path("matrix.csv"))

Dependencies: stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


# UTF-8 BOM. Prepended once before the CSV stream so Excel for Windows
# autodetects the encoding (RFC 3629 §6 is permissive on BOM usage).
_BOM = "﻿"


def write_csv(
    rows: Iterable[Mapping[str, object]],
    fieldnames: Sequence[str],
    out_path: Path,
    *,
    delimiter: str = ",",
    quoting: int = csv.QUOTE_MINIMAL,
) -> int:
    """Write *rows* to *out_path* as UTF-8 CSV with BOM.

    Returns the number of data rows written (header excluded).

    The function is deterministic: given the same iterable order, the same
    fieldnames, and the same dialect parameters, the output bytes are
    identical across invocations and platforms (CRLF line terminator pinned
    explicitly).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    # newline="" is mandatory per the csv module contract.
    # We force CRLF for Excel-on-Windows reproducibility.
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(_BOM)
        writer = csv.DictWriter(
            fh,
            fieldnames=list(fieldnames),
            delimiter=delimiter,
            quoting=quoting,
            lineterminator="\r\n",
            extrasaction="ignore",  # silently drop unknown keys
        )
        writer.writeheader()
        for row in rows:
            # Coerce non-string scalars (int, float, None) to a stable string.
            normalised = {k: _coerce(row.get(k)) for k in fieldnames}
            writer.writerow(normalised)
            written += 1

    return written


def _coerce(v: object) -> str:
    """Stable string coercion for CSV cells."""
    if v is None:
        return ""
    if isinstance(v, bool):
        # Avoid Python's "True"/"False" -- prefer the policy convention "yes"/"no".
        return "yes" if v else "no"
    if isinstance(v, float):
        # Strip trailing zeros for tabular compactness; keep up to 4 dp.
        return f"{v:.4f}".rstrip("0").rstrip(".") or "0"
    return str(v)


# --- Lever x actor x horizon canonical fieldnames ---------------------------

LEVER_FIELDS: tuple[str, ...] = (
    "lever_id",
    "title",
    "pillar",
    "actor",
    "horizon",
    "legal_ref",
    "cost_chf_mio",
    "feasibility_score",
    "claim_ids",
)


def write_lever_matrix(rows: Iterable[Mapping[str, object]], out_path: Path) -> int:
    """Convenience wrapper for the parliamentary lever matrix."""
    return write_csv(rows, LEVER_FIELDS, out_path)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Export parliamentary lever matrix as UTF-8 CSV with BOM.")
    p.add_argument("--rows", type=Path, required=True,
                   help="JSON file containing a list of dicts.")
    p.add_argument("--out", type=Path, required=True,
                   help="Destination .csv path.")
    p.add_argument("--fields", type=str, default=",".join(LEVER_FIELDS),
                   help="Comma-separated fieldnames (default: lever matrix schema).")
    args = p.parse_args()

    rows = json.loads(args.rows.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("--rows must be a JSON list of objects")
    fieldnames = [f.strip() for f in args.fields.split(",") if f.strip()]
    n = write_csv(rows, fieldnames, args.out)
    print(f"wrote {n} rows -> {args.out}")


if __name__ == "__main__":
    _cli()
