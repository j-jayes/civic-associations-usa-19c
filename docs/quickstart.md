# Quick Start Guide

This guide shows you how to use the civic-associations-usa-19c pipeline.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/j-jayes/civic-associations-usa-19c.git
cd civic-associations-usa-19c
```

2. Install the package:
```bash
pip install -e .
```

3. For development with all dependencies:
```bash
pip install -e ".[all]"
```

4. Set up your environment:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Pipeline Usage

The pipeline processes city directories through four main stages. Here's an example workflow for Boston 1855:

### 1. Build Manifest

First, organize your page images and create a manifest:

```bash
python scripts/build_manifest.py \
  --images-dir data/raw/boston_1855/images \
  --city "Boston" \
  --state "MA" \
  --year 1855 \
  --source-collection "boston_directory_1855"
```

This creates `data/raw/boston_1855/manifest.jsonl`.

### 2. Run OCR

Process the page images with OCR:

```bash
python scripts/run_ocr.py \
  --manifest data/raw/boston_1855/manifest.jsonl \
  --output-dir data/interim/ocr/boston_1855
```

This creates OCR text files in `data/interim/ocr/boston_1855/`.

### 3. Find Sections

Identify sections containing civic associations:

```bash
python scripts/find_sections.py \
  --ocr-dir data/interim/ocr/boston_1855 \
  --city "Boston" \
  --state "MA" \
  --year 1855 \
  --output data/interim/sections/boston_1855/sections.jsonl
```

### 4. Extract Associations

Use LLM to extract structured association records:

```bash
python scripts/extract_associations.py \
  --sections data/interim/sections/boston_1855/sections.jsonl \
  --output-dir data/interim/extractions/boston_1855 \
  --repeats 3
```

The `--repeats` flag runs extraction multiple times for verification.

### 5. Verify and Load

Verify consistency and load into database:

```bash
python scripts/verify_and_load.py \
  --extractions-dir data/interim/extractions/boston_1855 \
  --db-path data/processed/associations.sqlite
```

This creates:
- `data/processed/associations.sqlite` - Main database
- `data/processed/review_needed.jsonl` - Records needing manual review

### 6. Export for Analysis

Export data for analysis:

```bash
python scripts/export_for_analysis.py \
  --db-path data/processed/associations.sqlite \
  --output-dir data/processed/exports \
  --format csv
```

## Configuration

Configuration files in `config/` control various aspects:

- `project.yaml` - Paths, database URI, logging
- `ocr.yaml` - OCR engine settings
- `extraction.yaml` - LLM model and prompts
- `verification.yaml` - Quality thresholds

Edit these files to customize the pipeline behavior.

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=src/civic_associations --cov-report=html
```

## Analysis

Jupyter notebooks for analysis are in `notebooks/`:

1. `01_ocr_quality.ipynb` - Analyze OCR quality
2. `02_prompt_tuning.ipynb` - Tune LLM prompts
3. `03_analysis_networks.ipynb` - Network analysis of associations

Start Jupyter:

```bash
jupyter notebook notebooks/
```

## Project Structure

```
civic-associations-usa-19c/
├── config/              # Configuration files
├── data/                # Data directory (gitignored)
│   ├── raw/            # Source images and manifests
│   ├── interim/        # OCR outputs, sections, extractions
│   └── processed/      # Final database and exports
├── docs/                # Documentation
├── notebooks/           # Jupyter notebooks
├── scripts/             # Command-line scripts
├── src/                 # Source code
│   └── civic_associations/
│       ├── models/     # Pydantic models
│       ├── ingestion/  # Manifest building
│       ├── ocr/        # OCR processing
│       ├── extraction/ # LLM extraction
│       ├── verification/ # Quality checks
│       ├── db/         # Database operations
│       └── utils/      # Utilities
└── tests/               # Test suite
```

## Adding New Cities

To process a new city/year:

1. Place images in `data/raw/{collection}/images/`
2. Run the same pipeline with new parameters
3. All outputs go to collection-specific subdirectories

Example for New York 1860:

```bash
python scripts/build_manifest.py \
  --images-dir data/raw/ny_1860/images \
  --city "New York" \
  --state "NY" \
  --year 1860 \
  --source-collection "ny_directory_1860"

# Continue with remaining pipeline steps...
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:
```bash
pip install -e .
```

### Missing Dependencies

For OCR functionality:
```bash
pip install -e ".[ocr]"
```

For LLM extraction:
```bash
pip install -e ".[extraction]"
```

### Database Issues

If the database is locked or corrupted, you can recreate it by deleting and re-running verification:
```bash
rm data/processed/associations.sqlite
python scripts/verify_and_load.py ...
```

## Next Steps

1. Review the [architecture documentation](docs/architecture.md)
2. Check the [data dictionary](docs/data_dictionary.md)
3. Explore the example notebooks
4. Customize configuration for your needs

## Getting Help

- Read the documentation in `docs/`
- Check the test files for usage examples
- Review the README.md for project overview
