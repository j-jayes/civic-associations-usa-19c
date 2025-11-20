"""I/O utilities for reading and writing data files."""

import json
from pathlib import Path
from typing import List, Dict, Any, Iterator


def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """
    Read a JSONL file and return a list of dictionaries.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        List of dictionaries, one per line
    """
    data = []
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    
    return data


def write_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
    """
    Write a list of dictionaries to a JSONL file.
    
    Args:
        data: List of dictionaries to write
        file_path: Path to output JSONL file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')


def iter_jsonl(file_path: str) -> Iterator[Dict[str, Any]]:
    """
    Iterate over a JSONL file without loading all into memory.
    
    Args:
        file_path: Path to JSONL file
        
    Yields:
        Dictionary for each line
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
