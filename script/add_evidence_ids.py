#!/usr/bin/env python3
"""Annotate a mapped dataset with CIViC and PubMed evidence IDs from the masterlist.

For every row of the input TSV, the value of RAW_TERM is looked up against the
`biomarker` column of the masterlist. The `evidence_source` values of all
matching masterlist rows are collected and split by prefix: `CIViC:` values go
into a new `civic_id` column, `PubMed:` values into a new `pmid` column. Both
columns are inserted directly after SOURCE and hold pipe-separated values.

Usage: 
    python3 script/add_evidence_ids.py -i <input_tsv> -o <output_tsv>
E.g.:
    python3 script/add_evidence_ids.py -i data/mapped_processed/dataset_a_mapped.tsv -o data/mapped_processed/dataset_a_mapped_processed.tsv
"""

import argparse
import csv
import sys
from collections import defaultdict

CIVIC_PREFIX = "CIViC:"
PUBMED_PREFIX = "PubMed:"

# dataset_b contains Mac Roman curly quotes, dataset_a is plain UTF-8.
FALLBACK_ENCODINGS = ("utf-8", "mac_roman")


def open_text(path, encoding):
    """Open a TSV for reading, sniffing the encoding when asked to."""
    if encoding != "auto":
        return open(path, newline="", encoding=encoding)
    for enc in FALLBACK_ENCODINGS:
        try:
            with open(path, encoding=enc) as fh:
                fh.read()
        except UnicodeDecodeError:
            continue
        return open(path, newline="", encoding=enc)
    raise SystemExit(f"could not decode {path} as any of {FALLBACK_ENCODINGS}")


def find_column(header, name):
    """Return the index of `name` in `header`, ignoring case and surrounding space."""
    wanted = name.strip().lower()
    for i, field in enumerate(header):
        if field.strip().lower() == wanted:
            return i
    raise SystemExit(f"column {name!r} not found in header: {header}")


def build_index(masterlist_path, encoding):
    """Map each biomarker to its (civic_ids, pmids), de-duplicated, in file order."""
    index = defaultdict(lambda: ([], []))
    with open_text(masterlist_path, encoding) as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        biomarker_i = find_column(header, "biomarker")
        evidence_i = find_column(header, "evidence_source")
        for row in reader:
            if len(row) <= max(biomarker_i, evidence_i):
                continue
            biomarker = row[biomarker_i]
            if not biomarker:
                continue
            evidence = row[evidence_i].strip()
            civic_ids, pmids = index[biomarker]
            if evidence.startswith(CIVIC_PREFIX):
                bucket = civic_ids
            elif evidence.startswith(PUBMED_PREFIX):
                bucket = pmids
            else:
                continue
            # A biomarker repeats across masterlist rows, so the same evidence
            # source shows up many times; keep first occurrence only.
            if evidence not in bucket:
                bucket.append(evidence)
    return index


def process(input_path, output_path, index, encoding):
    with open_text(input_path, encoding) as fin:
        reader = csv.reader(fin, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            raise SystemExit(f"{input_path} is empty")

        source_i = find_column(header, "source")
        raw_term_i = find_column(header, "raw_term")
        insert_at = source_i + 1
        out_header = header[:insert_at] + ["civic_id", "pmid"] + header[insert_at:]

        total = matched = 0
        with open(output_path, "w", newline="", encoding="utf-8") as fout:
            writer = csv.writer(fout, delimiter="\t", lineterminator="\n")
            writer.writerow(out_header)
            for row in reader:
                total += 1
                # Pad short rows so the inserted columns stay aligned.
                if len(row) < len(header):
                    row = row + [""] * (len(header) - len(row))
                raw_term = row[raw_term_i]
                civic_ids, pmids = index.get(raw_term, ([], []))
                if civic_ids or pmids:
                    matched += 1
                writer.writerow(
                    row[:insert_at]
                    + ["|".join(civic_ids), "|".join(pmids)]
                    + row[insert_at:]
                )
    return total, matched


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input", required=True,
                        help="input mapped TSV (e.g. data/mapped_processed/dataset_a_mapped.tsv)")
    parser.add_argument("-o", "--output", required=True,
                        help="output TSV to write (e.g. data/mapped_processed/dataset_a_mapped_processed.tsv)")
    parser.add_argument("-m", "--masterlist",
                        default="data/mapped_processed/masterlist_v3.5.2.tsv",
                        help="masterlist TSV to look biomarkers up in (default: %(default)s)")
    parser.add_argument("-e", "--encoding", default="auto",
                        help="input encoding, or 'auto' to try utf-8 then mac_roman (default: %(default)s)")
    args = parser.parse_args()

    # Masterlist biomarkers can be long free text; lift the field size cap.
    csv.field_size_limit(sys.maxsize)

    index = build_index(args.masterlist, args.encoding)
    total, matched = process(args.input, args.output, index, args.encoding)
    print(f"{args.input} -> {args.output}: {matched}/{total} rows matched a biomarker "
          f"({len(index)} biomarkers indexed)")


if __name__ == "__main__":
    main()
