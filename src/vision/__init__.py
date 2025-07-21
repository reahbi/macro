"""
Vision module for image recognition and text extraction
"""

import logging
logger = logging.getLogger(__name__)

# Try to import vision modules with graceful fallback
try:
    from vision.image_matcher import ImageMatcher, MatchResult
except ImportError as e:
    logger.warning(f"ImageMatcher not available: {e}")
    ImageMatcher = None
    MatchResult = None

try:
    from vision.text_extractor import TextExtractor, TextResult
except ImportError as e:
    logger.warning(f"TextExtractor not available: {e}")
    TextExtractor = None
    TextResult = None

__all__ = ['ImageMatcher', 'MatchResult', 'TextExtractor', 'TextResult']