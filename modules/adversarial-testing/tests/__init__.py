"""
Test package for adversarial testing module.
"""
from pathlib import Path

# Define test constants
TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / 'test_data'
TEST_MODEL_DIR = TEST_DIR / 'test_models'

# Create directories if they don't exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_MODEL_DIR.mkdir(exist_ok=True)
