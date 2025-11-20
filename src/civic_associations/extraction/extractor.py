"""Extractor for processing sections and extracting associations."""

import json
import uuid
from typing import List
from ..models import Section, AssociationRecord, Member, ExtractionInput
from ..utils import setup_logger, make_association_id
from .llm_client import LLMClient
from .prompts import build_extraction_prompt

logger = setup_logger(__name__)


class Extractor:
    """Extract association records from sections using LLM."""
    
    def __init__(self, client: LLMClient):
        """
        Initialize extractor.
        
        Args:
            client: LLMClient instance
        """
        self.client = client
    
    def extract_from_section(
        self,
        section: Section,
        run_id: str = None,
        num_repeats: int = 1
    ) -> List[AssociationRecord]:
        """
        Extract association records from a section.
        
        Args:
            section: Section to process
            run_id: Extraction run ID
            num_repeats: Number of times to run extraction (for verification)
            
        Returns:
            List of AssociationRecord objects
        """
        if run_id is None:
            run_id = str(uuid.uuid4())
        
        logger.info(f"Extracting associations from section {section.section_id}")
        
        # Build prompts
        prompts = build_extraction_prompt(
            city=section.city,
            state=section.state,
            year=section.year,
            section_text=section.raw_text
        )
        
        # Call LLM
        response = self.client.call(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"]
        )
        
        # Parse response
        try:
            data = json.loads(response["content"])
            
            # Create AssociationRecord
            record = self._create_record(
                data=data,
                section=section,
                run_id=run_id,
                metadata={"model": response.get("model"), "tokens": response.get("tokens_used")}
            )
            
            return [record]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
    
    def _create_record(
        self,
        data: dict,
        section: Section,
        run_id: str,
        metadata: dict
    ) -> AssociationRecord:
        """Create an AssociationRecord from parsed data."""
        # Parse members
        members = []
        for m in data.get("members", []):
            members.append(Member(**m))
        
        # Create record
        record = AssociationRecord(
            association_id="",  # Will be set after
            name=data.get("name", "Unknown"),
            association_type=data.get("association_type"),
            city=section.city,
            state=section.state,
            year=section.year,
            source_collection=section.page_ids[0].rsplit("_p", 1)[0] if section.page_ids else "",
            source_pages=section.page_ids,
            raw_section_text=section.raw_text,
            members=members,
            extraction_run_id=run_id,
            metadata=metadata
        )
        
        # Generate association_id
        record.association_id = make_association_id(
            name=record.name,
            city=record.city or "",
            year=record.year or 0,
            source_pages=record.source_pages
        )
        
        return record
