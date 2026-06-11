# BiomarkerKB Volunteer Curation - 8-Week Project Roadmap

**Project goal:** Standardize non-compliant biomarker terms into structured `change | entity | aspect` components using the BiomarkerKB controlled vocabularies.  
**Team:** 2 volunteers (Cynthia, Dia)  
**Data split:** `terms4curation_a.csv` (Dataset A → Cynthia) and `terms4curation_b.csv` (Dataset B → Dia), swapped at Week 4 for cross-validation.

---

## Week 1 - Kickoff
**All hands**
- Introduce the BiomarkerKB project

---

## Week 2 - Onboarding & Orientation

**Documentation**
- Introduce volunteers to the BiomarkerKB curation system and the `change | entity | aspect` framework
- Walk through the three controlled vocabulary files (`change_type.txt`, `entity_type.txt`, `aspect_type.txt`) and their entry structures
- Review worked examples (e.g., "Increased Carcinoembryonic antigen (CEA)" → `increased | CEA | level`)
- Introduce the curation tools and data submission format
- Distribute datasets

**Deliverable:** Volunteers confirm they can parse at least 5 example biomarker terms correctly before proceeding.

---

## Week 3-4 - QC of Biomarker terms, Gap Analysis & Rule Proposals

**Cynthia** works on Dataset A | **Dia** works on Dataset B

- Manually normalize biomarker terms, assigning `change`, `entity`, and `aspect` from the controlled vocabularies
- For terms that don't fit any existing vocabulary entry, document the gap
- Draft candidate normalization rules for recurring patterns (e.g., HGVS-style mutation strings like `VHL (c.551T>C)`, gene deletion/loss-of-function phrases)
- Validate controlled vocabulary assignments against formal definitions paying close attention to tricky distinctions such as `level` vs. `expression`, `sequence variation` vs. `modification`, and `gene` vs. `DNA` vs. `protein`
- Run a log of edge cases and recurring patterns

**Deliverable:** Normalized mappings for unmapped terms + draft normalization rule proposals.

---

## Week 5 - Mid-Project Check-in & Dataset Swap

- Volunteers swap datasets: Cynthia now receives Dataset B; Dia receives Dataset A
- Each volunteer reviews the other's completed work independently - without reading their partner's notes first - to form unbiased initial impressions

**Deliverable:** Swap completed; each volunteer begins cross-validation with a fresh perspective.

---

## Week 6 - Cross-Validation & Reconciliation

**Cynthia** validates Dataset B | **Dia** validates Dataset A

- Re-examine the original curator's QC decisions and normalization choices
- Flag disagreements and record reasoning; note cases where approaches differ but both seem defensible
- Mid-week: share validation reports with each other and the project lead
- Discuss and resolve all flagged disagreements, finalizing all normalized biomarker mappings
- Consolidate normalization rule proposals into a clean, submission-ready document

**Deliverable:** Reconciled, finalized curation output + polished normalization rule proposals.

---

## Week 7 - Documentation & Wrap-up

**All hands**
- Final review of all outputs against project requirements
- Prepare a summary report covering:
  - Total biomarkers reviewed, normalized, and flagged
  - Key patterns and recurring problem types encountered
  - Proposed normalization rules with supporting examples
  - Remaining open questions or escalations
- Submit all materials to project lead
- Retrospective: what worked, what was unclear, what would help future volunteers

**Deliverable:** Complete curation package + summary report submitted.

---

## Week 8 - Symposium Prep

**Deliverable:** Oral presentation at the Volunteer Symposium (date&time TBD).

---

## Quick Reference: Key Decisions by Week

| Week | Primary Focus | Dataset Owner |
|------|--------------|---------------|
| 1-2 | Onboarding | Both |
| 3-4 | Unmapped biomarkers & rule proposals | A→A, B→B |
| 5 | Check-in + dataset swap | Both |
| 6 | Cross-validation & reconciliation | A→B, B→A |
| 7-8 | Documentation & wrap-up | Both |
