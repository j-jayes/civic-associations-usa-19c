"""OCR runner for batch processing pages."""

from pathlib import Path
from typing import List
from ..models import Page, PageOCR
from ..utils import setup_logger, read_jsonl
from .docling_client import DoclingClient

logger = setup_logger(__name__)


class OCRRunner:
    """Run OCR on a batch of pages."""
    
    def __init__(self, client: DoclingClient):
        """
        Initialize OCR runner.
        
        Args:
            client: DoclingClient instance
        """
        self.client = client
    
    def process_manifest(
        self,
        manifest_file: str,
        output_dir: str,
        batch_size: int = 10
    ) -> List[PageOCR]:
        """
        Process all pages from a manifest file.
        
        Args:
            manifest_file: Path to JSONL manifest
            output_dir: Directory to save OCR outputs
            batch_size: Number of pages to process at once
            
        Returns:
            List of PageOCR results
        """
        # Load manifest
        manifest_data = read_jsonl(manifest_file)
        pages = [Page(**item) for item in manifest_data]
        
        logger.info(f"Processing {len(pages)} pages from {manifest_file}")
        
        results = []
        for idx, page in enumerate(pages, start=1):
            logger.info(f"Processing page {idx}/{len(pages)}: {page.page_id}")
            
            try:
                result = self.client.process_page(page, output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {page.page_id}: {e}")
                continue
        
        logger.info(f"Completed OCR processing: {len(results)} successful")
        return results
