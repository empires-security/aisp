import os
from modelscan.modelscan import ModelScan

def run_modelscan(file_path: str):
    """
    Run ModelScan on the specified file and return the results.
    Args:
        file_path (str): Path to the serialized model file.
    Returns:
        dict: Scan results.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Initialize ModelScan
    scanner = ModelScan()

    # Run the scan
    results = scanner.scan(file_path)
    
    # print("Raw Scan Results:", results)

    # Return results as a dictionary
    return results
