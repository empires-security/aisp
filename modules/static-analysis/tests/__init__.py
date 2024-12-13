"""Test package for Static Analysis module."""

import os
from pathlib import Path
import tempfile
import json
from typing import Dict, Any

# Define test package constants
TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / 'test_data'
TEST_MODELS_DIR = TEST_DIR / 'test_models'

# Create necessary test directories
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_MODELS_DIR.mkdir(exist_ok=True)

class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    def create_test_model(format_type: str = 'pkl') -> Path:
        """
        Create a test model file.
        
        Args:
            format_type: Model file format extension
            
        Returns:
            Path: Path to created test file
        """
        test_file = TEST_MODELS_DIR / f'test_model.{format_type}'
        test_file.touch()
        return test_file

    @staticmethod
    def get_sample_result(status: str = 'safe') -> Dict[str, Any]:
        """
        Get a sample scan result dictionary.
        
        Args:
            status: Scan result status
            
        Returns:
            Dict: Sample scan result
        """
        return {
            "module": "StaticAnalysis",
            "file": "test_model.pkl",
            "endpoint": None,
            "status": status,
            "issues": [] if status == 'safe' else [
                {
                    "type": "error",
                    "description": "Test vulnerability found",
                    "severity": "HIGH",
                    "location": "line 1"
                }
            ],
            "metadata": {
                "file_name": "test_model.pkl",
                "scan_time": "0:00:01",
                "target": "file",
                "summary": "No issues found" if status == 'safe' else "Found 1 issue"
            }
        }

class TestBase:
    """Base class for test cases with common setup and teardown."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / 'test_model.pkl'
        self.test_file.touch()

    def tearDown(self):
        """Clean up test environment."""
        if self.test_file.exists():
            self.test_file.unlink()
        if Path(self.temp_dir).exists():
            Path(self.temp_dir).rmdir()

# Define common test data
SAMPLE_MODELS = {
    'pkl': TEST_MODELS_DIR / 'sample.pkl',
    'h5': TEST_MODELS_DIR / 'sample.h5',
    'pt': TEST_MODELS_DIR / 'sample.pt',
    'onnx': TEST_MODELS_DIR / 'sample.onnx'
}

SAMPLE_ISSUES = {
    'unsafe_import': {
        "type": "error",
        "description": "Unsafe module import detected",
        "severity": "HIGH",
        "location": "module.imports"
    },
    'malicious_code': {
        "type": "error",
        "description": "Potential malicious code detected",
        "severity": "CRITICAL",
        "location": "code.section"
    }
}

# Create sample test files if needed
for model_path in SAMPLE_MODELS.values():
    model_path.parent.mkdir(exist_ok=True)
    if not model_path.exists():
        model_path.touch()
