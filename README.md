## 1. Project goal (short + crisp)

Build a reproducible data pipeline that:

1. **Ingests** page images of 1th-century city/county directories.
2. **Performs OCR** and identifies directory sections listing civic associations.
3. **Extracts structured records** of associations (name, type, location, members, roles, etc.) using an LLM.
4. **Verifies** and **stores** these records in a queryable database (SQLite initially).

The design should be:

* **Re-usable:** easily switch to another city/year/source.
* **Auditable:** every record traceable back to the original page image and OCR text.
* **Modular:** each step can be swapped (new OCR engine, new LLM, new DB) with minimal pain.

**Working name:** `civic-associations-usa-19c`

* Association name
* Association type (temperance, hunting, masonic, etc.)
* Location (city, county, state, year)
* Members and positions
* Provenance: directory title + page(s), OCR text, extraction run info

**Core stages:**

1. **Ingestion** – get images + metadata into a clean manifest.
2. **OCR + Sectioning** – turn images → text; identify relevant sections.
3. **LLM Extraction** – parse sections into Pydantic models using Gemini 2.5-flash.
4. **Verification + Storage** – self-consistency checks, then store in SQLite.

**Important practical note:** Sites like ancestry.com have restrictive ToS and copyright constraints. The repo should treat input as “images living in `data/raw/` with a manifest” and keep scraping/acquisition logic out-of-scope or in a separate, clearly ToS-respecting step.

---

## 2. Data model (Pydantic)

Design this first; everything else flows into it.

```python
# src/civic_associations/models/association.py
from typing import List, Optional, Dict
from pydantic import BaseModel

class Member(BaseModel):
    full_name: str
    role: Optional[str] = None      # President, Treasurer, etc.
    notes: Optional[str] = None

class AssociationRecord(BaseModel):
    association_id: str             # stable hash (name+city+year+pages)
    name: str
    association_type: Optional[str] = None  # temperance, hunting, etc.

    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    year: Optional[int] = None

    source_directory_title: Optional[str] = None
    source_collection: Optional[str] = None  # e.g. "boston_directory_1855"
    source_pages: List[str] = []            # ["boston_1855_p012", "boston_1855_p013"]

    raw_section_text: str                   # text used for extraction
    members: List[Member] = []

    extraction_run_id: str
    metadata: Dict[str, object] = {}        # OCR confidence, model name, etc.
```

You’ll also want a `Page` and `Section` model.

```python
# src/civic_associations/models/page.py
class Page(BaseModel):
    page_id: str             # "boston_1855_p012"
    city: str
    county: Optional[str]
    state: str
    year: int
    source_collection: str   # "boston_directory_1855"
    page_number: int
    image_path: str          # "data/raw/boston_1855/images/boston_1855_p012.jpg"
    notes: Optional[str] = None

class Section(BaseModel):
    section_id: str                      # hash(page_ids + start_offset)
    page_ids: list[str]                  # one or more pages
    city: str
    state: str
    year: int
    start_page_number: int
    end_page_number: int
    section_type: str                    # "associations", "businesses", etc.
    raw_text: str
```

---

## 3. Repo layout (cookiecutter style)

Something like:

```bash
civic-associations-usa-19c/
├── README.md
├── pyproject.toml                # or setup.cfg/requirements.txt
├── .env.example
├── config/
│   ├── project.yaml              # base paths, db uri, etc.
│   ├── ocr.yaml                  # OCR engine config
│   ├── extraction.yaml           # LLM model + prompts
│   └── verification.yaml         # thresholds, repeats
├── data/                         # (mostly gitignored)
│   ├── raw/                      # images & manifests from sources
│   │   └── boston_1855/
│   ├── interim/                  # OCR outputs, sections, extractions
│   └── processed/                # final dbs, csvs, jsonl
├── notebooks/
│   ├── 01_ocr_quality.ipynb
│   ├── 02_prompt_tuning.ipynb
│   └── 03_analysis_networks.ipynb
├── src/
│   └── civic_associations/
│       ├── __init__.py
│       ├── config.py             # load YAML configs
│       ├── models/
│       │   ├── page.py
│       │   └── association.py
│       ├── ingestion/
│       │   ├── manifest_builder.py
│       │   └── file_naming.py
│       ├── ocr/
│       │   ├── docling_client.py
│       │   ├── ocr_runner.py
│       │   └── section_finder.py
│       ├── extraction/
│       │   ├── prompts.py
│       │   ├── llm_client.py
│       │   └── extractor.py
│       ├── verification/
│       │   ├── similarity.py
│       │   └── rules.py
│       ├── db/
│       │   ├── schema.py
│       │   └── writer.py
│       └── utils/
│           ├── hashing.py
│           ├── logging.py
│           └── io.py
├── scripts/
│   ├── build_manifest.py
│   ├── run_ocr.py
│   ├── find_sections.py
│   ├── extract_associations.py
│   ├── verify_and_load.py
│   └── export_for_analysis.py
├── tests/
│   ├── test_manifest_builder.py
│   ├── test_section_finder.py
│   ├── test_extractor.py
│   └── test_verification.py
└── docs/
    ├── architecture.md
    └── data_dictionary.md
```

This gives you:

* **Separation by step** (ingestion/ocr/extraction/verification/db).
* A clean place for **config**, **docs**, and **notebooks**.
* Clear `scripts/` for command-line entrypoints.

---

## 4. Step 1 – Ingestion

### 4.1 Inputs and assumptions

* You already have **directory images** for a given city/year, e.g.:
  `data/raw/boston_1855/images/boston_1855_p001.jpg`, etc.
* Either filenames encode page numbers, or you have a small CSV with metadata.

### 4.2 Manifest builder

`scripts/build_manifest.py`:

* CLI arguments:

  * `--images-dir`
  * `--city`, `--state`, `--year`
  * `--source-collection` (e.g. `boston_directory_1855`)
* Logic:

  * Enumerate images, sort by filename.
  * Infer `page_number` from filename or index order.
  * Create `Page` objects.
  * Save as JSONL manifest: `data/raw/boston_1855/manifest.jsonl`.

This step is pure plumbing and can be run per collection.

---

## 5. Step 2 – OCR + section detection

### 5.1 OCR with docling + RapidOCR

`src/civic_associations/ocr/docling_client.py` wraps your OCR stack:

* Input: `Page` + `image_path`.
* Output:

```python
class PageOCR(BaseModel):
    page_id: str
    text_md: str
    text_plain: str
    ocr_confidence: float
    blocks: list[dict] = []   # optional: block-level info from docling
```

`scripts/run_ocr.py`:

* Reads manifest.
* Runs OCR per page (with caching).
* Writes:

  * `data/interim/ocr/{collection}/{page_id}.md`
  * Optional JSONL summary: `ocr_results.jsonl`.

### 5.2 Section finder (civic associations subset)

We want to identify only the sections that list civic associations.

`src/civic_associations/ocr/section_finder.py`:

* Input: `PageOCR` objects in sequence.
* Heuristics:

  * Search for headings with keywords like “Societies”, “Associations”, “Lodges”, “Temperance”, “Hunting”, etc.
  * Use block structure: all-caps lines, bold, or separated by blank lines.
  * Group lines under association-related headings as candidate sections.
* Multi-page support:

  * If a section ends near the bottom of page N and page N+1 starts with similar line patterns (no new heading), merge into a single `Section` with `page_ids=[N, N+1, ...]`.

You can later refine this using an **LLM classifier** for borderline blocks: “Does this block belong to a civic association listing? YES/NO”.

Output:

* `data/interim/sections/{collection}/sections.jsonl` with `Section` objects.

---

## 6. Step 3 – LLM extraction

### 6.1 Design: text vs image mode

Define an interface that supports both:

```python
class ExtractionInput(BaseModel):
    section: Section
    ocr_text: str
    page_image_paths: list[str]
```

`config/extraction.yaml` controls mode:

```yaml
mode: "text"        # "multimodal" to also pass images
model_name: "gemini-2.5-flash"
temperature: 0.1
max_tokens: 4096
repeats: 3          # for verification/self-consistency
```

You can start with `mode: "text"` (Markdown from OCR) and experiment later.

### 6.2 Prompting and parsing

`src/civic_associations/extraction/prompts.py`:

* System prompt: explain context (18th-c US directories, civic associations).
* User prompt template:

  * Provide city, state, year, section text.
  * Ask for JSON conforming to `AssociationRecord` (minus `association_id`, which you’ll compute).
  * Provide 1–2 examples for prompt priming.

`src/civic_associations/extraction/llm_client.py`:

* Handles API calls to Gemini 2.5-flash (or other).
* Returns raw JSON.

`src/civic_associations/extraction/extractor.py`:

* Wraps the whole flow:

  * Build `ExtractionInput`.
  * Call LLM (possibly multiple times—see verification).
  * Parse JSON → `AssociationRecord` objects.
  * Compute `association_id` using a hash of normalized name, city, year, and pages:

```python
def make_association_id(record: AssociationRecord) -> str:
    key = f"{record.name.lower().strip()}|{record.city}|{record.year}|{'-'.join(sorted(record.source_pages))}"
    return some_hash(key)  # e.g. sha1/uuid5
```

Output:

* `data/interim/extractions/{collection}/run_{run_id}.jsonl`
  (each line: a Pydantic-serialised `AssociationRecord`).

---

## 7. Step 4 – Verification + SQLite

### 7.1 Multi-run self-consistency

You can implement “self-consistency” by running extraction K times per section (K from config).

For a given `section_id`:

* Collect K sets of `AssociationRecord`s.
* Compare:

  * **Exact agreement:** same set of associations with same names.
  * **Approx similarity:** fuzzy string match (Levenshtein / token set) on association names & member names.
  * **Field-majority voting:** for fields that differ (e.g. role “Chairman” vs “President”), take majority or mark uncertain.

Create a `VerificationResult` model:

```python
class VerificationResult(BaseModel):
    association_id: str
    num_runs: int
    exact_match_runs: int
    similarity_score: float
    status: str           # "accepted", "needs_review", "rejected"
    notes: Optional[str]
```

Rules (from `verification.yaml`):

```yaml
min_similarity: 0.9
min_exact_match_runs: 2
```

Records with low consistency go to a **review file** instead of the main DB.

### 7.2 SQLite schema and writer

`src/civic_associations/db/schema.py` defines:

```sql
CREATE TABLE associations (
  association_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  association_type TEXT,
  city TEXT,
  county TEXT,
  state TEXT,
  year INTEGER,
  source_directory_title TEXT,
  source_collection TEXT,
  raw_section_text TEXT,
  extraction_run_id TEXT,
  metadata_json TEXT
);

CREATE TABLE association_pages (
  association_id TEXT,
  page_id TEXT,
  PRIMARY KEY (association_id, page_id)
);

CREATE TABLE members (
  member_id INTEGER PRIMARY KEY AUTOINCREMENT,
  association_id TEXT,
  full_name TEXT NOT NULL,
  role TEXT,
  notes TEXT
);
```

`db/writer.py`:

* Opens SQLite connection (path from `project.yaml`).
* For each **accepted** `AssociationRecord`:

  * Insert into `associations` (upsert by `association_id`).
  * Insert into `association_pages`.
  * Insert members into `members`.

`verify_and_load.py` script:

* Reads all `run_*.jsonl` in an `extractions` folder.
* Performs consistency aggregation.
* Writes:

  * `data/processed/associations.sqlite`
  * `data/processed/review_needed.jsonl` (for manual QA).

---

## 8. Command-line workflow (per collection)

End-user (you) flow for e.g. Boston 1855:

```bash
# 1. Build manifest from images
python scripts/build_manifest.py \
  --images-dir data/raw/boston_1855/images \
  --city "Boston" \
  --state "MA" \
  --year 1855 \
  --source-collection "boston_directory_1855"

# 2. Run OCR
python scripts/run_ocr.py \
  --manifest data/raw/boston_1855/manifest.jsonl \
  --output-dir data/interim/ocr/boston_1855

# 3. Find sections (associations)
python scripts/find_sections.py \
  --ocr-dir data/interim/ocr/boston_1855 \
  --output data/interim/sections/boston_1855/sections.jsonl

# 4. Extract associations (possibly with repeats for verification)
python scripts/extract_associations.py \
  --sections data/interim/sections/boston_1855/sections.jsonl \
  --output-dir data/interim/extractions/boston_1855

# 5. Verify and load into SQLite
python scripts/verify_and_load.py \
  --extractions-dir data/interim/extractions/boston_1855 \
  --db-path data/processed/associations.sqlite
```

Everything is parameterised by **collection** (city+year), so adding more is just more runs of the same pipeline.

---

## 9. Development roadmap (for GitHub issues/milestones)

**Milestone 1 – Skeleton & models**

* [ ] Create repo + base structure (`src/`, `scripts/`, `config/`).
* [ ] Implement Pydantic models (`Page`, `Section`, `AssociationRecord`, `Member`).
* [ ] Implement basic config loader.
* [ ] Add initial README + docs/architecture.md (you can adapt this spec).

**Milestone 2 – Ingestion & OCR**

* [ ] `build_manifest.py` and tests.
* [ ] `docling_client.py` wrapper + `run_ocr.py`.
* [ ] Store OCR outputs and simple OCR-quality EDA notebook.

**Milestone 3 – Section detection**

* [ ] Implement `section_finder.py` (heuristics based).
* [ ] Add tests on a couple of hand-labelled pages.
* [ ] Write `find_sections.py` script.

**Milestone 4 – LLM extraction**

* [ ] Implement `llm_client.py` and config for Gemini 2.5-flash.
* [ ] Define prompts + `extractor.py`.
* [ ] Add tests with synthetic sample directory text.

**Milestone 5 – Verification & DB**

* [ ] Implement multi-run aggregation & similarity metrics.
* [ ] Create SQLite schema + `writer.py`.
* [ ] `verify_and_load.py` script and tests.

**Milestone 6 – Analysis & UX niceties**

* [ ] Notebook(s) exploring resulting data.
* [ ] Simple Streamlit or CLI browser for associations (optional).
* [ ] Better section finder (LLM classifier, etc.) if needed.

---

If you want, next step I can do is draft:

* A concrete `README.md` scaffold
* Example `config/*.yaml` files
  so you can literally initialise the repo and start committing.
