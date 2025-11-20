"""Docling OCR client wrapper."""

from pathlib import Path
from typing import Optional
from ..models import Page, PageOCR
from ..utils import setup_logger

logger = setup_logger(__name__)


class DoclingClient:
    """Wrapper for Docling OCR engine with RapidOCR backend."""
    
    def __init__(
        self,
        backend: str = "rapidocr",
        confidence_threshold: float = 0.5,
        output_format: str = "markdown"
    ):
        """
        Initialize Docling client.
        
        Args:
            backend: OCR backend to use
            confidence_threshold: Minimum confidence threshold
            output_format: Output format (markdown or plain)
        """
        self.backend = backend
        self.confidence_threshold = confidence_threshold
        self.output_format = output_format
        
        logger.info(f"Initialized DoclingClient with backend={backend}")
    
    def process_page(
        self,
        page: Page,
        output_dir: Optional[str] = None
    ) -> PageOCR:
        """
        Process a page image with OCR.
        
        Args:
            page: Page object with image path
            output_dir: Optional directory to save OCR output
            
        Returns:
            PageOCR object with results
        """
        image_path = Path(page.image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Processing page {page.page_id}")
        
        # TODO: Implement actual OCR processing with docling
        # For now, return a placeholder
        result = PageOCR(
            page_id=page.page_id,
            text_md="# Placeholder OCR text\n\nThis is a placeholder for OCR output.",
            text_plain="Placeholder OCR text\n\nThis is a placeholder for OCR output.",
            ocr_confidence=0.95,
            blocks=[]
        )
        
        # Save output if requested
        if output_dir:
            self._save_output(result, output_dir)
        
        return result
    
    def _save_output(self, result: PageOCR, output_dir: str) -> None:
        """Save OCR output to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save markdown
        md_file = output_path / f"{result.page_id}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(result.text_md)
        
        logger.debug(f"Saved OCR output to {md_file}")
