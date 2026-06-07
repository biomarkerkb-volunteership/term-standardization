# term-standardization
Volunteer curation guide for the BiomarkerKB project: instructions, controlled vocabulary reference, and submission guidelines.

# BiomarkerKB Volunteer Curation Documentation

Welcome, and thank you for contributing to the BiomarkerKB project! This documentation is organized into short sections you can refer back to at any point during the project. You don't need to read it all at once - use it as a reference as questions come up.

---

## Section 1 - How to Read a Biomarker Term

Every biomarker in BiomarkerKB is described as a combination of three components:
> Click the links below for full documentation on each component

| Component | Question it answers | Example |
|-----------|-------------------|---------|
| [**Change**](https://github.com/clinical-biomarkers/biomarker-controlled-vocabulary/blob/main/change_type.txt) | What happened to it? | *increased* |
| [**Entity**](https://github.com/clinical-biomarkers/biomarker-controlled-vocabulary/blob/main/entity_type.txt) | What is being measured? | *IL6* |
| [**Aspect**](https://github.com/clinical-biomarkers/biomarker-controlled-vocabulary/blob/main/aspect_type.txt) | What aspect of it was measured? | *level* |

So "Increased IL6 level" maps to: `increased | IL6 | level`

When you receive a raw biomarker term, your job is to decide whether it has been mapped to these three components correctly - and if not, to fix it or flag it.

**More examples:**

| Raw term | Change | Entity | Aspect |
|----------|--------|--------|--------|
| Decreased thyroid stimulating hormone | decreased | TSH | level |
| KLLN METHYLATION | presence of | KLLN | methylation |
| Increased Carcinoembryonic antigen (CEA) | increased | CEA | level |
| VHL (c.551T>C) | presence of | VHL | sequence variation |
| RB1 Loss-of-function | presence of | RB1 | sequence variation |

> **Note on missing components:** Sometimes a component is genuinely not stated in the raw term (e.g., no change direction given). In that case, use `differential` for change or `level` for aspect as a default, and add a note explaining your reasoning.

---

## Section 2 - Controlled Vocabulary Reference

You must use only the terms listed below when assigning each component. Do not invent new terms - if nothing fits, see Section 4 (Flagging & Escalation).

---

### Change Types

| Term | Use when… |
|------|-----------|
| **increased** | The entity's aspect is higher than normal |
| **decreased** | The entity's aspect is lower than normal |
| **presence of** | The entity or feature is present (binary) |
| **absence of** | The entity or feature is absent (binary) |
| **differential** | The direction of change is unstated or irrelevant |

**Common distinctions:**
- Use `increased`/`decreased` for anything on a scale (counts, levels, activity, copy number).
- Use `presence of`/`absence of` for binary outcomes - e.g., a specific mutation either is or isn't there.
- Use `differential` when a study reports something is "abnormal" or "altered" without specifying direction.

---

### Entity Types

| Term | What it covers |
|------|---------------|
| **protein** | Amino acid chains, including glycoproteins and protein complexes |
| **gene** | Specific regions of genetic material where sequence identity matters |
| **DNA** | DNA measured in bulk (e.g., cell-free DNA, methylation of a locus) |
| **RNA** | RNA or proxies of RNA expression (e.g., miRNA, mRNA) |
| **cell** | Individual cell types or cell-type ratios |
| **metabolite** | Small molecules involved in metabolism |
| **lipid** | Fats, oils, lipid-based molecules |
| **glycan** | Oligosaccharides or polysaccharides |
| **element** | Electrolytes, trace elements, toxic metals (e.g., sodium, iron, lead) |
| **image** | Entities evaluated via imaging (e.g., ground-glass opacity on CT) |

**Common distinctions:**
- A gene name (e.g., *BRCA2*) → `gene` if a specific sequence is being identified; `protein` if the translated product is being measured.
- Methylation of a DNA locus → `DNA` (not `gene`), aspect = `modification`.
- miRNA → `RNA`.
- Mixed entities (e.g., glycoproteins) can receive two entity type tags: both `protein` and `glycan`.

---

### Aspect Types

| Term | Use when… |
|------|-----------|
| **level** | A quantity is measured on a scale, but the precise aspect is unstated |
| **expression** | mRNA or protein is quantified, usually on a relative scale |
| **sequence variation** | A difference in sequence is observed (mutations, polymorphisms, deletions, insertions) |
| **modification** | A covalent or non-covalent change to a molecule is observed (e.g., methylation, phosphorylation, glycosylation) |

**Common distinctions:**
- Default to `level` when the raw term says things like "increased X" without further detail.
- Use `expression` when the measurement is explicitly about gene/protein expression (e.g., fold-change, overexpression).
- Use `sequence variation` for anything involving a specific mutation, SNP, deletion, insertion, or splice-site change.
- Use `modification` for epigenetic marks (methylation, acetylation) and post-translational modifications (phosphorylation, glycosylation). Always try to specify the modification type in the biomarker term rather than leaving it as a bare `modification`.

---

## Section 3 - Step-by-Step Curation Instructions

### Step 1 - Review the automated mapping
Each biomarker in your dataset will have an automated `change | entity | aspect` mapping already filled in. Start by reading the raw term and the proposed mapping side by side.

Ask yourself:
- Does the **change** term correctly reflect what is described?
- Is the **entity** correctly identified and named using its standard symbol or abbreviation?
- Is the **aspect** the most specific and accurate term available?

### Step 2 - Classify the mapping
Mark each mapping as one of the following:

| Status | Meaning |
|--------|---------|
| ✅ **Correct** | The automated mapping is accurate - no changes needed |
| ✏️ **Corrected** | You have fixed one or more components - fill in your corrected values |
| ❓ **Uncertain** | You are unsure of the correct mapping - flag for discussion |
| 🚩 **Unmapped / Cannot map** | The term cannot be mapped using the current vocabulary - propose a rule or escalate |

### Step 3 - For corrected mappings
Fill in the corrected `change`, `entity`, and `aspect` values in the designated columns. Always add a brief note explaining what was wrong and why you chose the new values.

### Step 4 - For unmapped or uncertain terms
See Section 4 below.

### Step 5 - Look for patterns
As you work, keep a running log of recurring problems (e.g., "all HGVS-style mutation strings like `VHL (c.551T>C)` are being mapped incorrectly"). These patterns will feed directly into normalization rule proposals in Week 3.

---

## Section 4 - Flagging, Uncertain Terms & Rule Proposals

### When to flag a term as uncertain
- The raw term is genuinely ambiguous and could map more than one way.
- You are unsure which entity type applies.
- The term uses language not covered by any vocabulary entry.

### When to propose a new normalization rule
If you see a **pattern** of terms that cannot be handled by the existing vocabulary, don't just flag each one individually - propose a rule. A good rule proposal includes:

1. **Pattern description** - What does this class of term look like? (e.g., "Gene name followed by an HGVS nucleotide change in parentheses")
2. **Example terms** - At least 2–3 real examples from your dataset
3. **Proposed mapping** - What should `change | entity | aspect` be for this pattern?
4. **Reasoning** - Why does this mapping make sense given the existing vocabulary definitions?

You do not need to be an ontology expert. Your job is to notice what doesn't fit and describe it clearly - the project lead will evaluate and formalize any new rules.

---

## Section 5 - How to Submit and Log Your Work

### Logging format
Use the provided curation spreadsheet. Each row corresponds to one biomarker term. The columns are:

| Column | What to fill in |
|--------|----------------|
| `raw_term` | The original biomarker string - do not edit this |
| `auto_change` | The automated change assignment - do not edit this |
| `auto_entity` | The automated entity assignment - do not edit this |
| `auto_aspect` | The automated aspect assignment - do not edit this |
| `status` | Your classification: Correct / Corrected / Uncertain / Unmapped |
| `curator_change` | Your corrected change value (if applicable) |
| `curator_entity` | Your corrected entity value (if applicable) |
| `curator_aspect` | Your corrected aspect value (if applicable) |
| `notes` | Your reasoning, especially for corrections and flags |

### Rule proposals
Log rule proposals in the separate **Rule Proposals** tab of the spreadsheet, following the format described in Section 4.

### Submission deadlines
Refer to the project schedule for weekly deliverable dates. If you are falling behind or have a question you cannot resolve, reach out to the project lead as early as possible - don't wait until the deadline.

---

## Quick Reference Card

```
CHANGE TYPES       increased | decreased | presence of | absence of | differential
ENTITY TYPES       protein | gene | DNA | RNA | cell | metabolite | lipid | glycan | element | image
ASPECT TYPES       level | expression | sequence variation | modification

STATUS CODES       ✅ Correct  ✏️ Corrected  ❓ Uncertain  🚩 Unmapped

GOLDEN RULE        If it doesn't fit, flag it and describe the pattern - don't force a mapping.
```
