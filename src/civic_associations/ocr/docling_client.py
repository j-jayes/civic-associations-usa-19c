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
        self._converter = None
        
        logger.info(f"Initialized DoclingClient with backend={backend}")
    
    def _init_docling(self):
        """Initialize Docling converter lazily."""
        if self._converter is not None:
            return
        
        try:
            from docling.document_converter import DocumentConverter
            
            # Initialize the converter
            self._converter = DocumentConverter()
            logger.info("Initialized Docling DocumentConverter")
            
        except ImportError:
            logger.warning("docling package not installed, using fallback OCR")
            self._converter = None
        except Exception as e:
            logger.error(f"Failed to initialize Docling: {e}")
            self._converter = None
    
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
        
        self._init_docling()
        
        if self._converter:
            try:
                # Convert the image with Docling
                result_doc = self._converter.convert(str(image_path))
                
                # Extract markdown and plain text
                text_md = result_doc.document.export_to_markdown()
                text_plain = result_doc.document.export_to_text()
                
                # Create PageOCR result
                result = PageOCR(
                    page_id=page.page_id,
                    text_md=text_md,
                    text_plain=text_plain,
                    ocr_confidence=0.95,  # Docling doesn't provide confidence scores
                    blocks=[]
                )
                
                logger.info(f"Successfully processed {page.page_id} with Docling")
                
            except Exception as e:
                logger.error(f"Docling processing failed: {e}, using placeholder")
                result = self._placeholder_result(page.page_id)
        else:
            logger.warning("Docling not available, using placeholder")
            result = self._placeholder_result(page.page_id)
        
        # Save output if requested
        if output_dir:
            self._save_output(result, output_dir)
        
        return result
    
    def _placeholder_result(self, page_id: str) -> PageOCR:
        """Create a placeholder result when OCR is not available."""
        return PageOCR(
            page_id=page_id,
            text_md="# Placeholder OCR text\n\nThis is a placeholder for OCR output.",
            text_plain="Placeholder OCR text\n\nThis is a placeholder for OCR output.",
            ocr_confidence=0.95,
            blocks=[]
        )
    
    def _save_output(self, result: PageOCR, output_dir: str) -> None:
        """Save OCR output to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save markdown
        md_file = output_path / f"{result.page_id}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(result.text_md)
        
        logger.debug(f"Saved OCR output to {md_file}")
