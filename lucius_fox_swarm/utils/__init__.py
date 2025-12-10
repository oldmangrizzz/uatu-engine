"""
Utility functions for the Lucius Fox Swarm Framework.
"""
import re
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Convert to lowercase
    sanitized = sanitized.lower()
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def format_currency(amount: Optional[float], currency: str = "USD") -> str:
    """
    Format a currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    if currency == "USD":
        symbol = "$"
    else:
        symbol = currency + " "
    
    # Format with commas
    if amount >= 1_000_000_000:
        return f"{symbol}{amount/1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"{symbol}{amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{symbol}{amount/1_000:.2f}K"
    else:
        return f"{symbol}{amount:.2f}"


def extract_year(text: str) -> Optional[int]:
    """
    Extract a year from text.
    
    Args:
        text: Text potentially containing a year
        
    Returns:
        Extracted year or None
    """
    # Look for 4-digit years (1900-2099)
    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        return int(match.group(0))
    return None


def calculate_confidence_score(data_points: int, sources: int) -> float:
    """
    Calculate a confidence score based on data availability.
    
    Args:
        data_points: Number of data points gathered
        sources: Number of unique sources
        
    Returns:
        Confidence score (0-100)
    """
    # Base score from data points (max 70%)
    data_score = min(data_points * 5, 70)
    
    # Source diversity score (max 30%)
    source_score = min(sources * 6, 30)
    
    return min(data_score + source_score, 100.0)
