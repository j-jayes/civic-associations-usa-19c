# Architecture

This document describes the architecture of the civic-associations-usa-19c data pipeline.

## Overview

The pipeline extracts structured civic association records from 19th-century US city directories through four main stages:

1. **Ingestion**: Organize page images and create manifests
2. **OCR + Sectioning**: Convert images to text and identify relevant sections
3. **LLM Extraction**: Extract structured association records using language models
4. **Verification + Storage**: Validate records and store in SQLite database

## Design Principles

### Modularity
Each stage is independent and can be swapped out:
- Different OCR engines (Docling, Tesseract, etc.)
- Different LLM providers (Gemini, OpenAI, local models)
- Different storage backends (SQLite, PostgreSQL, etc.)

### Reproducibility
Every record is traceable:
- Source page images and filenames preserved
- OCR text stored with extractions
- Extraction run IDs track processing history
- Configuration files version control settings

### Re-usability
Adding new cities/years requires only:
1. Place images in `data/raw/{collection}/images/`
2. Run the same pipeline scripts with new parameters

## Data Flow

```
images/ → manifest.jsonl → OCR → sections.jsonl → LLM extraction → verification → database
  ↓                          ↓                       ↓                              ↓
raw/                      interim/ocr/          interim/extractions/          processed/
```

### Stage 1: Ingestion

**Input**: Directory of page images
**Output**: `manifest.jsonl` with Page objects
**Script**: `scripts/build_manifest.py`

Creates a structured manifest of all pages with metadata (city, state, year, page numbers).

### Stage 2: OCR + Sectioning

**Input**: Manifest + images
**Output**: OCR text (markdown) + `sections.jsonl`
**Scripts**: `scripts/run_ocr.py`, `scripts/find_sections.py`

- OCR processes each page image
- Section finder identifies civic association sections using keywords/heuristics
- Can span multiple pages

### Stage 3: LLM Extraction

**Input**: `sections.jsonl`
**Output**: `run_{id}.jsonl` with AssociationRecord objects
**Script**: `scripts/extract_associations.py`

- For each section, prompts LLM to extract:
  - Association name and type
  - Members and roles
  - Location information
- Supports multiple runs per section for self-consistency checking

### Stage 4: Verification + Storage

**Input**: Multiple extraction runs
**Output**: SQLite database + review files
**Script**: `scripts/verify_and_load.py`

- Aggregates multiple extraction runs
- Checks self-consistency (exact matches, similarity)
- Validates records (required fields, format)
- Stores accepted records in database
- Flags uncertain records for manual review

## Database Schema

### associations
Main table storing association records with full metadata and provenance.

### association_pages
Junction table linking associations to source pages (many-to-many).

### members
Member records linked to associations (one-to-many).

## Configuration

Configuration is split across YAML files in `config/`:

- `project.yaml`: Paths, database URI, logging
- `ocr.yaml`: OCR engine settings
- `extraction.yaml`: LLM model, prompts, verification settings
- `verification.yaml`: Similarity thresholds, quality rules

## Extension Points

### Custom OCR Engines
Implement `DoclingClient` interface in `src/civic_associations/ocr/`

### Custom LLM Providers
Implement `LLMClient` interface in `src/civic_associations/extraction/`

### Custom Section Finders
Extend `SectionFinder` class for better heuristics or ML-based detection

### Custom Verification Rules
Add rules in `src/civic_associations/verification/rules.py`

## Testing Strategy

- Unit tests for utilities (hashing, I/O, config)
- Integration tests for each pipeline stage
- End-to-end tests with sample data
- Fixtures for common test data patterns

## Future Enhancements

1. **Multimodal extraction**: Pass page images directly to LLM
2. **Active learning**: Use uncertainty to prioritize manual review
3. **Network analysis**: Build association/membership graphs
4. **Web interface**: Browse and search associations
5. **Incremental processing**: Skip already-processed pages
