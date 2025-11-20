"""Pydantic models for civic associations data pipeline."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Member(BaseModel):
    """Association member with role information."""
    full_name: str
    role: Optional[str] = None
    notes: Optional[str] = None


class AssociationRecord(BaseModel):
    """Complete association record with members and provenance."""
    association_id: str
    name: str
    association_type: Optional[str] = None
    
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    year: Optional[int] = None
    
    source_directory_title: Optional[str] = None
    source_collection: Optional[str] = None
    source_pages: List[str] = Field(default_factory=list)
    
    raw_section_text: str
    members: List[Member] = Field(default_factory=list)
    
    extraction_run_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Page(BaseModel):
    """Single page from a directory with metadata."""
    page_id: str
    city: str
    county: Optional[str] = None
    state: str
    year: int
    source_collection: str
    page_number: int
    image_path: str
    notes: Optional[str] = None


class PageOCR(BaseModel):
    """OCR results for a single page."""
    page_id: str
    text_md: str
    text_plain: str
    ocr_confidence: float = 0.0
    blocks: List[Dict[str, Any]] = Field(default_factory=list)


class Section(BaseModel):
    """Section of text spanning one or more pages."""
    section_id: str
    page_ids: List[str]
    city: str
    state: str
    year: int
    start_page_number: int
    end_page_number: int
    section_type: str
    raw_text: str


class ExtractionInput(BaseModel):
    """Input for LLM extraction."""
    section: Section
    ocr_text: str
    page_image_paths: List[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    """Verification result for an association record."""
    association_id: str
    num_runs: int
    exact_match_runs: int
    similarity_score: float
    status: str  # "accepted", "needs_review", "rejected"
    notes: Optional[str] = None
