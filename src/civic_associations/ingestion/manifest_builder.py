"""Manifest builder for creating page manifests from image directories."""

from pathlib import Path
from typing import List, Optional
from ..models import Page
from ..utils import setup_logger

logger = setup_logger(__name__)


class ManifestBuilder:
    """Build page manifests from directory images."""
    
    def __init__(
        self,
        city: str,
        state: str,
        year: int,
        source_collection: str,
        county: Optional[str] = None
    ):
        """
        Initialize manifest builder.
        
        Args:
            city: City name
            state: State abbreviation
            year: Year of directory
            source_collection: Collection identifier
            county: Optional county name
        """
        self.city = city
        self.state = state
        self.year = year
        self.source_collection = source_collection
        self.county = county
    
    def build_from_directory(
        self,
        images_dir: str,
        output_file: str
    ) -> List[Page]:
        """
        Build manifest from a directory of images.
        
        Args:
            images_dir: Path to directory containing images
            output_file: Path to output JSONL manifest file
            
        Returns:
            List of Page objects
        """
        images_path = Path(images_dir)
        
        if not images_path.exists():
            raise FileNotFoundError(f"Images directory not found: {images_dir}")
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
        image_files = sorted([
            f for f in images_path.iterdir()
            if f.suffix.lower() in image_extensions
        ])
        
        logger.info(f"Found {len(image_files)} images in {images_dir}")
        
        # Build Page objects
        pages = []
        for idx, image_file in enumerate(image_files, start=1):
            page_id = self._generate_page_id(image_file.stem, idx)
            
            page = Page(
                page_id=page_id,
                city=self.city,
                county=self.county,
                state=self.state,
                year=self.year,
                source_collection=self.source_collection,
                page_number=idx,
                image_path=str(image_file)
            )
            pages.append(page)
        
        # Save to JSONL
        self._save_manifest(pages, output_file)
        
        logger.info(f"Created manifest with {len(pages)} pages: {output_file}")
        return pages
    
    def _generate_page_id(self, filename: str, page_number: int) -> str:
        """Generate a page ID from filename or page number."""
        # If filename already contains page info, use it
        # Otherwise, construct from collection and page number
        if '_p' in filename:
            return filename
        else:
            return f"{self.source_collection}_p{page_number:03d}"
    
    def _save_manifest(self, pages: List[Page], output_file: str) -> None:
        """Save pages to JSONL manifest."""
        from ..utils import write_jsonl
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionaries
        data = [page.model_dump() for page in pages]
        write_jsonl(data, output_file)
