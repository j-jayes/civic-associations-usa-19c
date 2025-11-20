#!/usr/bin/env python3
"""Build manifest from directory images."""

import argparse
from pathlib import Path
from civic_associations.ingestion import ManifestBuilder
from civic_associations.utils import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Build page manifest from directory images"
    )
    parser.add_argument(
        "--images-dir",
        required=True,
        help="Directory containing page images"
    )
    parser.add_argument(
        "--city",
        required=True,
        help="City name"
    )
    parser.add_argument(
        "--state",
        required=True,
        help="State abbreviation (e.g., MA, NY)"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Directory year"
    )
    parser.add_argument(
        "--source-collection",
        required=True,
        help="Collection identifier (e.g., boston_directory_1855)"
    )
    parser.add_argument(
        "--county",
        help="County name (optional)"
    )
    parser.add_argument(
        "--output",
        help="Output manifest file path (default: <images-dir>/manifest.jsonl)"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_file = args.output
    else:
        output_file = str(Path(args.images_dir) / "manifest.jsonl")
    
    logger.info(f"Building manifest for {args.source_collection}")
    
    # Build manifest
    builder = ManifestBuilder(
        city=args.city,
        state=args.state,
        year=args.year,
        source_collection=args.source_collection,
        county=args.county
    )
    
    pages = builder.build_from_directory(args.images_dir, output_file)
    
    logger.info(f"Created manifest with {len(pages)} pages: {output_file}")


if __name__ == "__main__":
    main()
