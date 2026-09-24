# Data Cleanup Post Volunteer Review

## Steps

- Copied `data/mapped/dataset_a_cynthia.xlsx` and `data/mapped/dataset_b_cynthia.xlsx` to `data/mapped_processed/`.
- Extracted the tab `Repeated Terms-No repeated terms` from both xlsx files to `dataset_a_processed.tsv` and `dataset_b_processed.tsv` respectively.
- Added two columns: `civic_id` and `pmid` and populated them using annotations from `masterlist_v3.5.2.tsv`
  ```
  python3 script/add_evidence_ids.py -i data/mapped_processed/dataset_a_mapped.tsv -o data/mapped_processed/dataset_a_mapped_processed.tsv
  python3 script/add_evidence_ids.py -i data/mapped_processed/dataset_b_mapped.tsv -o data/mapped_processed/dataset_b_mapped_processed.tsv
  ```
- Overwrote all values under column `type` or `TYPE` to "level" if source is `llm_glycan`.

## Issues

- There are rows with many `civid_id`s and `pmid`s.
- There will be significant information lost for some rows. E.g., biomarker `VHL (c.194C>G)` if mapped to `presence of VHL gene	sequence variation`, the a.a. substitution context will be completely lost. Such info is critical for genomic variation data.
- Some unicode/(ascii) characters are lost from raw source and are unrecoverable. E.g., `_-glucans associated with immunoglobulin M` (dataset A Line 4), `ALK C1156Y�L1198F` (a Ln579), `with a concentration of 22 _ mol/L in healthy infants` (masterlist Ln806122)
- Some nt/a.a. substitution biomarkers can actually be mapped. E.g., `civic	CIViC:1567	PubMed:27433843	JAK1 Q503*					cannot map	No pattern matched` (b Ln127) - /\* is a wildcard, it only means Q503 is substituted by any other a.a..
