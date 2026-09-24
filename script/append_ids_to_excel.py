"""
append_civic_ids.py
-------------------
Joins CIViC IDs and PMIDs from a TSV onto the Excel workbook produced by
Cynthia's curation, and writes a new workbook with all original sheets preserved.

Usage:
    python append_civic_ids.py \
        --tsv   path/to/curated_civic.tsv \
        --excel "Dataset A by Cynthia（final version）.xlsx" \
        --out   "Dataset_A_with_IDs.xlsx"

The TSV is expected to have exactly 10 tab-separated columns:
    0  source       
    1  civic_ids    (e.g. "CIViC:447" or "CIViC:495|CIViC:4311")
    2  pmids        (e.g. "PubMed:22906996" or "PubMed:21345110|PubMed:28787259")
    3  raw_term
    4  change
    5  entity
    6  entity_type
    7  aspect
    8  status
    9  notes

The script joins on raw_term and inserts civic_ids + pmids as the 2nd and 3rd
columns (right after source) in both civic-containing sheets.
"""

import argparse
import sys
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tsv",   required=True, help="Path to the TSV file with CIViC IDs and PMIDs")
    p.add_argument("--excel", required=True, help="Path to the source Excel workbook")
    p.add_argument("--out",   required=True, help="Path for the output Excel workbook")
    p.add_argument("--sheets", nargs="+",
                   default=["Curated Terms-No repeated terms", "Curated Terms"],
                   help="Sheet name(s) to enrich (default: both curated-terms sheets)")
    return p.parse_args()

# ---------------------------------------------------------------------------
# TSV loader
# ---------------------------------------------------------------------------

# Canonical column names after reading the header.
# The TSV header uses "civic_id" and "pmid" (singular); we rename them
# to "civic_ids" / "pmids" so they match the new Excel column headers.
TSV_RENAME = {"civic_id": "civic_ids", "pmid": "pmids",
              "entity type": "entity_type"}

def load_tsv(path: str) -> pd.DataFrame:
    """Read the headered TSV and return a lookup keyed on raw_term."""
    df = pd.read_csv(path, sep="\t", header=0,
                     dtype=str, keep_default_na=False)
    df = df.rename(columns=TSV_RENAME)
    df = df[df["SOURCE"] == "civic"].copy()

    # Deduplicate on raw_term — keep the first occurrence.
    # (The TSV should already be deduplicated, but guard against edge cases.)
    dupes = df.duplicated(subset="RAW_TERM", keep=False)
    if dupes.any():
        dup_terms = df.loc[dupes, "raw_term"].unique().tolist()
        print(f"  Warning: {len(dup_terms)} raw_term(s) appear more than once in the TSV; "
              f"keeping first occurrence.\n  Examples: {dup_terms[:5]}")
        df = df.drop_duplicates(subset="raw_term", keep="first")

    lookup = df.set_index("RAW_TERM")[["civic_ids", "pmids"]]
    print(f"  TSV: loaded {len(lookup)} unique civic raw_terms.")
    return lookup

# ---------------------------------------------------------------------------
# Sheet enrichment
# ---------------------------------------------------------------------------

def enrich_sheet(df: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join civic_ids and pmids onto df, inserting them after the
    'source' column.  Non-civic rows get empty strings.
    """
    # Only join for civic rows; leave llm_glycan rows blank.
    civic_mask = df["SOURCE"] == "civic"
    joined = df.join(lookup, on="RAW_TERM", how="left")

    # Fill non-civic rows with empty strings (they have no CIViC data).
    joined.loc[~civic_mask, ["civic_ids", "pmids"]] = ""
    joined[["civic_ids", "pmids"]] = joined[["civic_ids", "pmids"]].fillna("")

    # Reorder: source | civic_ids | pmids | raw_term | ...rest
    cols = list(df.columns)
    src_idx = cols.index("SOURCE")
    new_order = (cols[: src_idx + 1]         # up to and including "source"
                 + ["civic_ids", "pmids"]
                 + cols[src_idx + 1 :])       # everything after "source"
    return joined[new_order]

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report_unmatched(df_enriched: pd.DataFrame, sheet_name: str):
    civic_rows = df_enriched[df_enriched["SOURCE"] == "civic"]
    unmatched = civic_rows[civic_rows["civic_ids"] == ""]
    if unmatched.empty:
        print(f"  '{sheet_name}': all civic rows matched — no gaps.")
    else:
        print(f"  '{sheet_name}': {len(unmatched)} civic row(s) had NO match in the TSV:")
        for term in unmatched["raw_term"].tolist():
            print(f"    • {term}")

# ---------------------------------------------------------------------------
# Excel writer (preserves all sheets)
# ---------------------------------------------------------------------------

HEADER_FILL  = PatternFill("solid", fgColor="DCE6F1")   # light blue
NEW_COL_FILL = PatternFill("solid", fgColor="E2EFDA")   # light green — marks the new columns
HEADER_FONT  = Font(name="Arial", bold=True, size=10)
BODY_FONT    = Font(name="Arial", size=10)


def style_header_cell(cell, is_new: bool = False):
    cell.font = HEADER_FONT
    cell.fill = NEW_COL_FILL if is_new else HEADER_FILL
    cell.alignment = Alignment(wrap_text=True, vertical="center")


def write_sheet(ws, df: pd.DataFrame, new_cols: list[str]):
    """Write df to an (already cleared) worksheet with light styling."""
    # Header row
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        style_header_cell(cell, is_new=(col_name in new_cols))

    # Data rows
    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx,
                           value="" if (value is None or str(value) == "nan") else value)
            cell.font = BODY_FONT
            cell.alignment = Alignment(wrap_text=False, vertical="top")

    # Auto-size columns (capped so notes column doesn't explode)
    MAX_WIDTH = 60
    for col_idx, col_name in enumerate(df.columns, start=1):
        col_values = [str(col_name)] + [
            str(v) if v is not None else "" for v in df.iloc[:, col_idx - 1]
        ]
        best_width = min(max(len(v) for v in col_values) + 2, MAX_WIDTH)
        ws.column_dimensions[get_column_letter(col_idx)].width = best_width

    ws.freeze_panes = "A2"   # keep header visible while scrolling


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    print(f"\nLoading TSV: {args.tsv}")
    lookup = load_tsv(args.tsv)

    print(f"\nLoading Excel: {args.excel}")
    xl = pd.ExcelFile(args.excel)
    all_sheet_names = xl.sheet_names
    print(f"  Sheets found: {all_sheet_names}")

    # Validate requested sheets exist
    for name in args.sheets:
        if name not in all_sheet_names:
            print(f"  ERROR: sheet '{name}' not found in workbook. "
                  f"Available: {all_sheet_names}")
            sys.exit(1)

    # Read and enrich each target sheet
    enriched: dict[str, pd.DataFrame | None] = {}
    new_cols = ["civic_ids", "pmids"]

    for name in all_sheet_names:
        if name in args.sheets:
            print(f"\nEnriching sheet: '{name}'")
            df = xl.parse(name, dtype=str).fillna("")
            df_enriched = enrich_sheet(df, lookup)
            report_unmatched(df_enriched, name)
            enriched[name] = df_enriched
        else:
            enriched[name] = None   # will be copied unchanged

    # Write output workbook
    print(f"\nWriting output: {args.out}")
    wb_src = load_workbook(args.excel)   # keep original sheets we won't touch

    for name in all_sheet_names:
        ws = wb_src[name]
        df_new = enriched[name]

        if df_new is not None:
            # Clear and rewrite this sheet
            ws.delete_rows(1, ws.max_row)
            write_sheet(ws, df_new, new_cols)
            print(f"  Wrote '{name}': {len(df_new)} rows × {len(df_new.columns)} columns.")
        else:
            print(f"  Kept '{name}' unchanged.")

    wb_src.save(args.out)
    print(f"\nDone.  Output saved to: {args.out}\n")


if __name__ == "__main__":
    main()
