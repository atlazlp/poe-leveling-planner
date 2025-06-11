#!/usr/bin/env python3
"""
HTML Parser Utilities
Provides graceful fallback for BeautifulSoup parsers when lxml is not available
"""

from bs4 import BeautifulSoup
import warnings

# Test which parsers are available
AVAILABLE_PARSERS = []

# Test lxml
try:
    import lxml
    AVAILABLE_PARSERS.append('lxml')
except ImportError:
    pass

# html.parser is always available (built into Python)
AVAILABLE_PARSERS.append('html.parser')

# Test html5lib (optional, better for malformed HTML)
try:
    import html5lib
    AVAILABLE_PARSERS.append('html5lib')
except ImportError:
    pass

# Select the best available parser
PREFERRED_PARSER = AVAILABLE_PARSERS[0]

def get_soup(content, parser=None):
    """
    Create a BeautifulSoup object with the best available parser
    
    Args:
        content: HTML content (string or bytes)
        parser: Specific parser to use (optional)
        
    Returns:
        BeautifulSoup object
    """
    if parser and parser in AVAILABLE_PARSERS:
        try:
            return BeautifulSoup(content, parser)
        except Exception as e:
            warnings.warn(f"Failed to use {parser} parser: {e}. Falling back to {PREFERRED_PARSER}")
    
    # Use the preferred parser
    try:
        return BeautifulSoup(content, PREFERRED_PARSER)
    except Exception as e:
        # Final fallback to html.parser
        if PREFERRED_PARSER != 'html.parser':
            warnings.warn(f"Failed to use {PREFERRED_PARSER} parser: {e}. Falling back to html.parser")
            return BeautifulSoup(content, 'html.parser')
        else:
            raise e

def get_preferred_parser():
    """Get the name of the preferred parser"""
    return PREFERRED_PARSER

def get_available_parsers():
    """Get list of available parsers"""
    return AVAILABLE_PARSERS.copy()

def print_parser_info():
    """Print information about available parsers"""
    print("HTML Parser Information:")
    print(f"  Preferred parser: {PREFERRED_PARSER}")
    print(f"  Available parsers: {', '.join(AVAILABLE_PARSERS)}")
    
    if 'lxml' in AVAILABLE_PARSERS:
        print("  ✓ lxml is available (fastest parser)")
    else:
        print("  ✗ lxml not available (will use html.parser - slower but compatible)")
    
    if 'html5lib' in AVAILABLE_PARSERS:
        print("  ✓ html5lib is available (best for malformed HTML)")
    else:
        print("  ✗ html5lib not available") 