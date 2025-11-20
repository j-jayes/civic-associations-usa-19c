"""Configuration loading utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load a configuration file from the config directory.
    
    Args:
        config_name: Name of the config file (without .yaml extension)
        
    Returns:
        Dictionary containing configuration data
    """
    config_path = Path(__file__).parent.parent.parent / "config" / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_data_dir(subdir: str = "") -> Path:
    """
    Get a data directory path.
    
    Args:
        subdir: Subdirectory within data/ (e.g., "raw", "interim", "processed")
        
    Returns:
        Path to the data directory
    """
    data_dir = get_project_root() / "data"
    if subdir:
        data_dir = data_dir / subdir
    return data_dir
