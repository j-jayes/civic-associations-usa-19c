"""Prompt building for LLM extraction."""

from typing import Dict, Any


def build_extraction_prompt(
    city: str,
    state: str,
    year: int,
    section_text: str,
    system_prompt: str = None
) -> Dict[str, str]:
    """
    Build prompts for association extraction.
    
    Args:
        city: City name
        state: State abbreviation
        year: Year
        section_text: Raw OCR text of section
        system_prompt: Optional custom system prompt
        
    Returns:
        Dictionary with 'system' and 'user' prompts
    """
    if system_prompt is None:
        system_prompt = """You are an expert at extracting structured data from 19th-century US city directories.
You will be given sections from civic association listings and must extract:
- Association name
- Association type (temperance, masonic, hunting, etc.)
- Members and their roles

Return the data as valid JSON conforming to this structure:
{
  "name": "Association Name",
  "association_type": "type",
  "members": [
    {"full_name": "Name", "role": "Position"}
  ]
}

Focus on accuracy and completeness. If a field is unclear, omit it rather than guessing."""
    
    user_prompt = f"""Extract civic association information from this directory section.

Location: {city}, {state}
Year: {year}

Section text:
{section_text}

Return valid JSON with the association information."""
    
    return {
        "system": system_prompt,
        "user": user_prompt
    }
