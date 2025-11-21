#!/usr/bin/env python3
"""Extract associations from sections using LLM."""

import argparse
import uuid
from pathlib import Path

from civic_associations.config import load_config
from civic_associations.extraction import Extractor, LLMClient
from civic_associations.models import Section
from civic_associations.utils import read_jsonl, setup_logger, write_jsonl

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Extract associations from sections using LLM"
    )
    parser.add_argument(
        "--sections",
        required=True,
        help="Path to sections JSONL file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save extraction outputs"
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Number of extraction runs per section (for verification)"
    )
    parser.add_argument(
        "--run-id",
        help="Extraction run ID (auto-generated if not provided)"
    )

    args = parser.parse_args()

    # Generate run ID if not provided
    run_id = args.run_id or str(uuid.uuid4())[:8]

    logger.info(f"Starting extraction run: {run_id}")

    # Load extraction config
    try:
        config = load_config("extraction")
        llm_config = config.get("extraction", {}).get("llm", {})
    except Exception:
        logger.warning("Could not load extraction config, using defaults")
        llm_config = {}

    # Initialize client and extractor
    client = LLMClient(
        model_name=llm_config.get("model_name", "gemini-2.0-flash-exp"),
        temperature=llm_config.get("temperature", 0.1),
        max_tokens=llm_config.get("max_tokens", 4096)
    )

    extractor = Extractor(client)

    # Load sections
    sections_data = read_jsonl(args.sections)
    sections = [Section(**s) for s in sections_data]

    logger.info(f"Processing {len(sections)} sections")

    # Extract associations
    all_records = []
    for idx, section in enumerate(sections, start=1):
        logger.info(f"Processing section {idx}/{len(sections)}: {section.section_id}")

        records = extractor.extract_from_section(
            section=section,
            run_id=run_id,
            num_repeats=args.repeats
        )

        all_records.extend(records)

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"run_{run_id}.jsonl"
    records_data = [r.model_dump() for r in all_records]
    write_jsonl(records_data, str(output_file))

    logger.info(f"Extracted {len(all_records)} associations, saved to {output_file}")


if __name__ == "__main__":
    main()
