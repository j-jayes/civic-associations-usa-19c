# Data Dictionary

This document describes the data structures used in the civic-associations-usa-19c pipeline.

## Page

Represents a single page from a directory source.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page_id | string | Yes | Unique page identifier (e.g., "boston_1855_p012") |
| city | string | Yes | City name |
| county | string | No | County name |
| state | string | Yes | State abbreviation (e.g., "MA") |
| year | integer | Yes | Directory publication year |
| source_collection | string | Yes | Collection identifier (e.g., "boston_directory_1855") |
| page_number | integer | Yes | Sequential page number |
| image_path | string | Yes | Path to page image file |
| notes | string | No | Optional notes about the page |

## PageOCR

OCR results for a single page.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page_id | string | Yes | Page identifier (matches Page.page_id) |
| text_md | string | Yes | OCR text in Markdown format |
| text_plain | string | Yes | OCR text in plain format |
| ocr_confidence | float | Yes | Overall OCR confidence (0.0-1.0) |
| blocks | list[dict] | No | Block-level OCR info from engine |

## Section

Represents a section within one or more pages.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| section_id | string | Yes | Unique section identifier (hash) |
| page_ids | list[string] | Yes | Page IDs in this section |
| city | string | Yes | City name |
| state | string | Yes | State abbreviation |
| year | integer | Yes | Directory year |
| start_page_number | integer | Yes | First page number |
| end_page_number | integer | Yes | Last page number |
| section_type | string | Yes | Section type (e.g., "associations") |
| raw_text | string | Yes | Full text of the section |

## Member

Represents a member of an association.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| full_name | string | Yes | Member's full name |
| role | string | No | Role/position (e.g., "President", "Secretary") |
| notes | string | No | Additional notes about the member |

## AssociationRecord

Complete association record extracted from a directory.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| association_id | string | Yes | Stable hash ID (name+city+year+pages) |
| name | string | Yes | Association name |
| association_type | string | No | Association type (e.g., "temperance", "masonic") |
| city | string | No | City name |
| county | string | No | County name |
| state | string | No | State abbreviation |
| year | integer | No | Directory year |
| source_directory_title | string | No | Full title of source directory |
| source_collection | string | No | Collection identifier |
| source_pages | list[string] | Yes | Source page IDs |
| raw_section_text | string | Yes | Original OCR text used for extraction |
| members | list[Member] | No | List of association members |
| extraction_run_id | string | Yes | ID of extraction run |
| metadata | dict | No | Additional metadata (model name, tokens, etc.) |

## ExtractionInput

Input data for LLM extraction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| section | Section | Yes | Section to extract from |
| ocr_text | string | Yes | OCR text (plain or markdown) |
| page_image_paths | list[string] | Yes | Paths to page images (for multimodal) |

## VerificationResult

Results from verification/self-consistency checks.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| association_id | string | Yes | Association identifier |
| num_runs | integer | Yes | Total number of extraction runs |
| exact_match_runs | integer | Yes | Number of exactly matching runs |
| similarity_score | float | Yes | Average similarity score (0.0-1.0) |
| status | string | Yes | "accepted", "needs_review", or "rejected" |
| notes | string | No | Additional notes about verification |

## Database Schema

### associations table

Stores association records.

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
```

### association_pages table

Links associations to source pages (many-to-many).

```sql
CREATE TABLE association_pages (
    association_id TEXT,
    page_id TEXT,
    PRIMARY KEY (association_id, page_id),
    FOREIGN KEY (association_id) REFERENCES associations(association_id)
);
```

### members table

Stores association members.

```sql
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    association_id TEXT,
    full_name TEXT NOT NULL,
    role TEXT,
    notes TEXT,
    FOREIGN KEY (association_id) REFERENCES associations(association_id)
);
```

## Association Types

Common association types found in 19th-century directories:

- **temperance**: Temperance societies, anti-alcohol organizations
- **masonic**: Masonic lodges and related fraternal orders
- **hunting**: Hunting and fishing clubs
- **benevolent**: Charitable and mutual aid societies
- **fraternal**: General fraternal organizations
- **professional**: Professional associations (medical, legal, etc.)
- **social**: Social clubs and societies
- **veterans**: Military veterans organizations
- **religious**: Religious societies and groups
- **cultural**: Literary, musical, and cultural societies

## File Formats

### JSONL (JSON Lines)

All intermediate data is stored in JSONL format:
- One JSON object per line
- Easy to stream and process incrementally
- Human-readable and git-friendly

### Markdown

OCR output is stored in Markdown for:
- Preservation of structure (headings, lists)
- Human readability
- Easy conversion to other formats

### SQLite

Final database uses SQLite for:
- Zero-configuration deployment
- ACID transactions
- Full SQL query capabilities
- Easy backup and portability
