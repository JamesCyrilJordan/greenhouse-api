"""
Tests for app/__main__.py module entry point.
"""
import pytest
import subprocess
import sys
from pathlib import Path


class TestMainModule:
    """Tests for the __main__ module entry point."""
    
    def test_main_module_can_be_imported(self):
        """Test that __main__ module can be imported."""
        # This tests that the module structure is correct
        from app import __main__
        assert hasattr(__main__, "__name__")
    
    def test_main_module_has_main_block(self):
        """Test that __main__ has the if __name__ == '__main__' block."""
        # Read the file to verify it exists (indirect test)
        main_file = Path(__file__).parent.parent / "app" / "__main__.py"
        content = main_file.read_text()
        assert "if __name__" in content
        assert "__main__" in content

