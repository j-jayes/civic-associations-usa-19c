#!/usr/bin/env python3
"""Run OCR on page images from a manifest."""

import argparse
from civic_associations.ocr import DoclingClient, OCRRunner
from civic_associations.utils import setup_logger
from civic_associations.config import load_config

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Run OCR on pages from manifest"
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to manifest JSONL file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save OCR outputs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for processing (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Load OCR config
    try:
        config = load_config("ocr")
        docling_config = config.get("ocr", {}).get("docling", {})
    except:
        logger.warning("Could not load OCR config, using defaults")
        docling_config = {}
    
    logger.info(f"Processing manifest: {args.manifest}")
    
    # Initialize client and runner
    client = DoclingClient(
        backend=docling_config.get("backend", "rapidocr"),
        confidence_threshold=docling_config.get("confidence_threshold", 0.5),
        output_format=docling_config.get("output_format", "markdown")
    )
    
    runner = OCRRunner(client)
    
    # Process manifest
    results = runner.process_manifest(
        manifest_file=args.manifest,
        output_dir=args.output_dir,
        batch_size=args.batch_size
    )
    
    logger.info(f"Completed OCR processing: {len(results)} pages processed")


if __name__ == "__main__":
    main()
