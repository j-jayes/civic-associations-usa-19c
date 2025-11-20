# GitHub Actions Test Workflow

This document describes the automated testing workflow for the civic associations extraction pipeline.

## Overview

The workflow `test-docling-extraction.yml` provides automated testing of the complete data pipeline:
1. **Manifest Building** - Catalogs images and creates metadata
2. **OCR Processing** - Extracts text from images using Docling
3. **Section Finding** - Identifies civic association sections
4. **LLM Extraction** - Extracts structured data using Gemini

## Triggers

The workflow can be triggered in two ways:

### Manual Trigger
Use the GitHub Actions UI to run the workflow manually:
```
Actions → Test Docling OCR and Extraction Pipeline → Run workflow
```

You can optionally specify a collection name (default: `buffalo_1862`).

### Automatic Trigger
The workflow automatically runs when:
- New images are added to `data/raw/*/images/`
- The workflow file itself is modified

## What It Does

### 1. Environment Setup
- Python 3.12
- System dependencies for image processing
- Required packages: docling, google-generativeai, pillow, pyyaml

### 2. Pipeline Execution
Runs all four stages of the pipeline on test images with comprehensive logging.

### 3. Output Management
- **Saves to repository**: Commits all outputs to the branch
  - OCR results: `data/interim/ocr/{collection}/`
  - Sections: `data/interim/sections/{collection}/`
  - Extractions: `data/interim/extractions/{collection}/`
  - Logs: `logs/`
  
- **Uploads artifacts**: 30-day retention for inspection
  - All pipeline outputs
  - Complete logs
  - Summary report

### 4. Summary Report
Generates `logs/pipeline_summary.md` with:
- Input/output counts
- Sample outputs from each stage
- Links to full logs
- Status of each pipeline step

## Viewing Results

### In the Repository
After the workflow completes, check the branch for:
```
data/interim/ocr/buffalo_1862/*.md        # OCR text
data/interim/sections/buffalo_1862/sections.jsonl  # Sections
data/interim/extractions/buffalo_1862/run_*.jsonl  # Associations
logs/pipeline_summary.md                   # Summary
```

### In Workflow Artifacts
1. Go to the workflow run in GitHub Actions
2. Scroll to "Artifacts" section
3. Download `pipeline-outputs-{collection}`

### In Workflow Summary
The workflow automatically adds a summary to the GitHub Actions run page with key metrics and sample outputs.

## Configuration

The workflow uses repository secrets:
- `GEMINI_API_KEY` - Required for LLM extraction

## Testing Locally

To test the pipeline locally before pushing:

```bash
# 1. Set up environment
export GEMINI_API_KEY="your-key-here"
pip install -e .
pip install docling google-generativeai pillow pyyaml

# 2. Run pipeline steps
python scripts/build_manifest.py \
  --images-dir data/raw/buffalo_1862/images \
  --city Buffalo --state NY --year 1862 \
  --source-collection buffalo_1862

python scripts/run_ocr.py \
  --manifest data/raw/buffalo_1862/manifest.jsonl \
  --output-dir data/interim/ocr/buffalo_1862

python scripts/find_sections.py \
  --ocr-dir data/interim/ocr/buffalo_1862 \
  --city Buffalo --state NY --year 1862 \
  --output data/interim/sections/buffalo_1862/sections.jsonl

python scripts/extract_associations.py \
  --sections data/interim/sections/buffalo_1862/sections.jsonl \
  --output-dir data/interim/extractions/buffalo_1862
```

## Debugging

Each step generates a log file in the `logs/` directory:
- `01_build_manifest.log`
- `02_run_ocr.log`
- `03_find_sections.log`
- `04_extract_associations.log`

Check these logs for detailed error messages and debugging information.

## Adding New Test Collections

To test with a different city/year:

1. Add images to `data/raw/{city}_{year}/images/`
2. Run the workflow with custom collection name
3. Or push to trigger automatic detection

The workflow will automatically:
- Parse the collection name to extract city and year
- Run the full pipeline
- Commit outputs to the appropriate directories

## Design Rationale

**Why commit outputs to the repository?**
- Immediate visibility of results
- Easy inspection and comparison
- Version control of test data
- No need to download artifacts for quick checks

**Why also upload artifacts?**
- Redundancy if commit fails
- Easy bulk download
- Keeps artifacts separate from code
- 30-day retention for review

**Why manual and automatic triggers?**
- Manual: Test on-demand during development
- Automatic: Continuous validation when images added
- Flexibility for different workflows
