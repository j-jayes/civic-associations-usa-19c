#!/usr/bin/env python3
"""Find association sections in OCR output."""

import argparse
from pathlib import Path
from civic_associations.ocr import SectionFinder
from civic_associations.models import PageOCR
from civic_associations.utils import setup_logger, read_jsonl, write_jsonl

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Find association sections in OCR output"
    )
    parser.add_argument(
        "--ocr-dir",
        required=True,
        help="Directory containing OCR markdown files"
    )
    parser.add_argument(
        "--manifest",
        help="Path to original manifest (for metadata)"
    )
    parser.add_argument(
        "--city",
        required=True,
        help="City name"
    )
    parser.add_argument(
        "--state",
        required=True,
        help="State abbreviation"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Directory year"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output sections JSONL file"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Finding sections in OCR directory: {args.ocr_dir}")
    
    # Load OCR results
    ocr_dir = Path(args.ocr_dir)
    ocr_files = sorted(ocr_dir.glob("*.md"))
    
    logger.info(f"Found {len(ocr_files)} OCR files")
    
    # Create PageOCR objects from files
    ocr_results = []
    for ocr_file in ocr_files:
        page_id = ocr_file.stem
        with open(ocr_file, 'r', encoding='utf-8') as f:
            text_md = f.read()
        
        # Simple plain text conversion
        text_plain = text_md.replace("#", "").replace("*", "")
        
        ocr_results.append(PageOCR(
            page_id=page_id,
            text_md=text_md,
            text_plain=text_plain,
            ocr_confidence=0.95,
            blocks=[]
        ))
    
    # Find sections
    finder = SectionFinder()
    sections = finder.find_sections(
        ocr_results=ocr_results,
        city=args.city,
        state=args.state,
        year=args.year
    )
    
    # Save sections
    sections_data = [s.model_dump() for s in sections]
    write_jsonl(sections_data, args.output)
    
    logger.info(f"Found {len(sections)} sections, saved to {args.output}")


if __name__ == "__main__":
    main()
