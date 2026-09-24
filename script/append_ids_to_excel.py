"""
append_ids_to_excel.py
-------------------
Joins CIViC IDs and PMIDs from one or more TSVs onto the Excel workbook
produced by Cynthia's curation, and writes a new workbook with all original
sheets preserved.

Usage (single TSV, old behaviour):
    python append_ids_to_excel.py \
        --tsvs  path/to/curated_civic.tsv \
        --excel "Dataset A by Cynthia（final version）.xlsx" \
        --out   "Dataset_A_with_IDs.xlsx"

Usage (multiple source-specific TSVs):
    python append_ids_to_excel.py \
        --tsvs dataset_b_pmc.tsv dataset_b_cgi.tsv dataset_b_mw.tsv \
               dataset_b_oncomx.tsv dataset_b_upkb.tsv \
        --excel "Dataset A by Cynthia（final version）.xlsx" \
        --out   "Dataset_A_with_IDs.xlsx"

Each TSV is expected to have tab-separated columns including at minimum:
    SOURCE       — must match the SOURCE column in the Excel sheet
    RAW_TERM     — join key
    civic_ids    (or civic_id)
    pmids        (or pmid)

All TSVs are concatenated and the lookup is keyed on (SOURCE, RAW_TERM),
so the same raw_term can exist under different sources without collision.
PMIDs are expected not to overlap across files (each file owns its source).
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
    # *** CHANGED: nargs="+" so you can pass one or many TSV paths ***
    p.add_argument("--tsvs", nargs="+", required=True,
                   help="One or more TSV files with CIViC IDs and PMIDs "
                        "(e.g. dataset_b_pmc.tsv dataset_b_cgi.tsv …)")
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
TSV_RENAME = {"civic_id": "civic_ids", "pmid": "pmids",
              "entity type": "entity_type"}

def load_tsvs(paths: list) -> pd.DataFrame:
    """
    Read and concatenate one or more headered TSVs.

    Returns a DataFrame indexed on (SOURCE, RAW_TERM) with columns
    ['civic_ids', 'pmids'].  The SOURCE filter that previously restricted
    lookup to 'civic' rows has been removed — every row in every TSV is
    a valid lookup target, keyed to whichever SOURCE it declares.
    """
    frames = []
    for path in paths:
        df = pd.read_csv(path, sep="\t", header=0,
                         dtype=str, keep_default_na=False)
        df = df.rename(columns=TSV_RENAME)
        # Normalise column names to upper-case so they match the Excel sheets
        df.columns = [c.upper() if c in ("source", "SOURCE") else c for c in df.columns]
        frames.append(df)
        print(f"    {path}: {len(df)} rows")

    combined = pd.concat(frames, ignore_index=True)
    print(f"  TSV total: {len(combined)} rows across {len(paths)} file(s).")

    # Deduplicate so no (source, raw_term) pair appears more than once.
    dupes = combined.duplicated(subset=["source", "raw_term"], keep=False)
    if dupes.any():
        dup_pairs = (combined.loc[dupes, ["source", "raw_term"]]
                     .drop_duplicates().head(5).to_dict("records"))
        print(f"  Warning: duplicated (source, raw_term) pairs detected; "
              f"keeping first occurrence.\n  Examples: {dup_pairs}")
        combined = combined.drop_duplicates(subset=["source", "raw_term"], keep="first")

    lookup = combined.set_index(["source", "raw_term"])[["civic_ids", "pmids"]]
    print(f"  Lookup built: {len(lookup)} unique (source, raw_term) pairs.")
    return lookup

# ---------------------------------------------------------------------------
# Sheet enrichment
# ---------------------------------------------------------------------------

def enrich_sheet(df: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join civic_ids and pmids onto df using (source, raw_term) as the
    composite key, then insert the two new columns right after source.
    Rows with no match in the lookup receive empty strings.
    """
    lookup_reset = lookup.reset_index()   # source, raw_term, civic_ids, pmids

    merged = df.merge(
        lookup_reset[["source", "raw_term", "civic_ids", "pmids"]],
        on=["source", "raw_term"],
        how="left",
    )
    merged[["civic_ids", "pmids"]] = merged[["civic_ids", "pmids"]].fillna("")

    # Reorder: source | civic_ids | pmids | raw_term | …rest
    cols = list(df.columns)
    src_idx = cols.index("source")
    new_order = (cols[: src_idx + 1]
                 + ["civic_ids", "pmids"]
                 + cols[src_idx + 1 :])
    return merged[new_order]

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report_unmatched(df_enriched: pd.DataFrame, sheet_name: str):
    """Print rows that had no PMID match, grouped by source."""
    unmatched = df_enriched[df_enriched["civic_ids"] == ""]
    if unmatched.empty:
        print(f"  '{sheet_name}': all rows matched — no gaps.")
        return

    by_source = unmatched.groupby("source")["raw_term"].apply(list)
    print(f"  '{sheet_name}': {len(unmatched)} row(s) had NO match in the TSVs:")
    for src, terms in by_source.items():
        print(f"    [{src}] {len(terms)} term(s) — e.g. {terms[:3]}")

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


def write_sheet(ws, df: pd.DataFrame, new_cols: list):
    """Write df to an (already cleared) worksheet with light styling."""
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        style_header_cell(cell, is_new=(col_name in new_cols))

    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx,
                           value="" if (value is None or str(value) == "nan") else value)
            cell.font = BODY_FONT
            cell.alignment = Alignment(wrap_text=False, vertical="top")

    MAX_WIDTH = 60
    for col_idx, col_name in enumerate(df.columns, start=1):
        col_values = [str(col_name)] + [
            str(v) if v is not None else "" for v in df.iloc[:, col_idx - 1]
        ]
        best_width = min(max(len(v) for v in col_values) + 2, MAX_WIDTH)
        ws.column_dimensions[get_column_letter(col_idx)].width = best_width

    ws.freeze_panes = "A2"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    print(f"\nLoading TSV(s):")
    lookup = load_tsvs(args.tsvs)

    print(f"\nLoading Excel: {args.excel}")
    xl = pd.ExcelFile(args.excel)
    all_sheet_names = xl.sheet_names
    print(f"  Sheets found: {all_sheet_names}")

    for name in args.sheets:
        if name not in all_sheet_names:
            print(f"  ERROR: sheet '{name}' not found. Available: {all_sheet_names}")
            sys.exit(1)

    enriched: dict = {}
    new_cols = ["civic_ids", "pmids"]

    for name in all_sheet_names:
        if name in args.sheets:
            print(f"\nEnriching sheet: '{name}'")
            df = xl.parse(name, dtype=str).fillna("")
            df_enriched = enrich_sheet(df, lookup)
            report_unmatched(df_enriched, name)
            enriched[name] = df_enriched
        else:
            enriched[name] = None

    print(f"\nWriting output: {args.out}")
    wb_src = load_workbook(args.excel)

    for name in all_sheet_names:
        ws = wb_src[name]
        df_new = enriched[name]

        if df_new is not None:
            ws.delete_rows(1, ws.max_row)
            write_sheet(ws, df_new, new_cols)
            print(f"  Wrote '{name}': {len(df_new)} rows × {len(df_new.columns)} columns.")
        else:
            print(f"  Kept '{name}' unchanged.")

    wb_src.save(args.out)
    print(f"\nDone.  Output saved to: {args.out}\n")


if __name__ == "__main__":
    main()
