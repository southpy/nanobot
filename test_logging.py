#!/usr/bin/env python3
"""Test script to verify logging configuration."""

from nanobot.utils.logging import configure_logging, configure_file_logging
from loguru import logger


def test_logging_levels():
    """Test different logging levels."""
    print("\n=== Testing WARNING level (default) ===")
    configure_logging(verbose=False, debug=False)
    logger.debug("This is a DEBUG message (should NOT appear)")
    logger.info("This is an INFO message (should NOT appear)")
    logger.warning("This is a WARNING message (should appear)")
    logger.error("This is an ERROR message (should appear)")
    
    print("\n=== Testing INFO level (--verbose) ===")
    configure_logging(verbose=True, debug=False)
    logger.debug("This is a DEBUG message (should NOT appear)")
    logger.info("This is an INFO message (should appear)")
    logger.warning("This is a WARNING message (should appear)")
    logger.error("This is an ERROR message (should appear)")
    
    print("\n=== Testing DEBUG level (--debug) ===")
    configure_logging(verbose=False, debug=True)
    logger.debug("This is a DEBUG message (should appear)")
    logger.info("This is an INFO message (should appear)")
    logger.warning("This is a WARNING message (should appear)")
    logger.error("This is an ERROR message (should appear)")


def test_file_logging():
    """Test file logging."""
    import tempfile
    import os
    
    print("\n=== Testing file logging ===")
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
    temp_file.close()
    
    try:
        configure_logging(verbose=True, debug=False)
        configure_file_logging(temp_file.name, level="DEBUG")
        
        logger.info("This message should appear in both console and file")
        logger.debug("This DEBUG message should only appear in file")
        
        # Read file content
        with open(temp_file.name, 'r') as f:
            content = f.read()
        
        print(f"\nFile content ({temp_file.name}):")
        print(content)
        
        # Verify
        assert "This message should appear in both console and file" in content
        assert "This DEBUG message should only appear in file" in content
        print("\n✓ File logging test passed!")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


if __name__ == "__main__":
    print("🐈 nanobot Logging Test\n")
    test_logging_levels()
    test_file_logging()
    print("\n✓ All tests passed!")

