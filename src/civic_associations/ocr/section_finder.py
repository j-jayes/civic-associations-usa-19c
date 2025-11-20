"""Section finder for identifying civic association sections."""

from typing import List
from ..models import PageOCR, Section
from ..utils import setup_logger, make_section_id

logger = setup_logger(__name__)


class SectionFinder:
    """Find sections containing civic associations in OCR text."""
    
    def __init__(self, keywords: List[str] = None):
        """
        Initialize section finder.
        
        Args:
            keywords: List of keywords to identify association sections
        """
        self.keywords = keywords or [
            "societies",
            "associations",
            "lodges",
            "temperance",
            "hunting",
            "masonic",
            "fraternal",
            "benevolent",
        ]
        logger.info(f"Initialized SectionFinder with {len(self.keywords)} keywords")
    
    def find_sections(
        self,
        ocr_results: List[PageOCR],
        city: str,
        state: str,
        year: int
    ) -> List[Section]:
        """
        Find association sections in OCR results.
        
        Args:
            ocr_results: List of PageOCR results
            city: City name
            state: State abbreviation
            year: Year
            
        Returns:
            List of Section objects
        """
        logger.info(f"Finding sections in {len(ocr_results)} pages")
        
        sections = []
        
        # TODO: Implement actual section detection logic
        # For now, create a placeholder section
        if ocr_results:
            first_page = ocr_results[0]
            last_page = ocr_results[-1]
            
            page_ids = [r.page_id for r in ocr_results]
            section_id = make_section_id(page_ids, 0)
            
            section = Section(
                section_id=section_id,
                page_ids=page_ids,
                city=city,
                state=state,
                year=year,
                start_page_number=1,
                end_page_number=len(ocr_results),
                section_type="associations",
                raw_text="\n\n".join([r.text_plain for r in ocr_results])
            )
            sections.append(section)
        
        logger.info(f"Found {len(sections)} sections")
        return sections
