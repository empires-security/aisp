import os
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging
from modelscan.modelscan import ModelScan
from modelscan.error import ModelScanError, PathError
from modelscan.issues import IssueSeverity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelScanner:
    def __init__(self):
        self.scanner = ModelScan()
        
    def _map_severity(self, severity: str) -> str:
        severity_mapping = {
            'CRITICAL': 'error',
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'warning'
        }
        return severity_mapping.get(severity, 'warning')

    def scan_file(self, file_path: Union[str, Path]) -> Dict:
        """
        Scan a model file for security issues using ModelScan.
        """
        try:
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            
            # Basic validation
            if not file_path.exists():
                raise FileNotFoundError(f"Model file not found: {file_path}")
            
            if not self.scanner.is_compatible(str(file_path)):
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Perform the scan
            scan_start = datetime.now()
            try:
                results = self.scanner.scan(file_path)
            except Exception as scan_error:
                # Handle scan errors explicitly
                return {
                    "module": "StaticAnalysis",
                    "file": str(file_path),
                    "endpoint": None,
                    "status": "error",
                    "issues": [{
                        "type": "error",
                        "description": str(scan_error),
                        "severity": "CRITICAL",
                        "location": "N/A"
                    }],
                    "metadata": {
                        "file_name": file_path.name,
                        "scan_time": "N/A",
                        "target": "file",
                        "summary": f"Scan operation failed: {str(scan_error)}"
                    }
                }
            
            scan_end = datetime.now()
            
            # Process results
            issues = []
            
            # Check for errors in results
            if results.get('errors'):
                # Convert errors to issues
                for error in results['errors']:
                    issues.append({
                        "type": "error",
                        "description": error.get('message', 'Unknown error'),
                        "severity": "CRITICAL",
                        "location": error.get('source', 'N/A')
                    })
                # Return error result immediately
                return {
                    "module": "StaticAnalysis",
                    "file": str(file_path),
                    "endpoint": None,
                    "status": "error",
                    "issues": issues,
                    "metadata": {
                        "file_name": file_path.name,
                        "scan_time": str(scan_end - scan_start),
                        "target": "file",
                        "summary": "Scan completed with errors"
                    }
                }
            
            # Process regular issues if no errors
            if results.get('issues'):
                for issue in results['issues']:
                    issues.append({
                        "type": self._map_severity(issue.get('severity', 'LOW')),
                        "description": issue.get('description', 'No description provided'),
                        "severity": issue.get('severity', 'LOW'),
                        "location": issue.get('source', 'N/A')
                    })
            
            # Return normal result
            return {
                "module": "StaticAnalysis",
                "file": str(file_path),
                "endpoint": None,
                "status": 'unsafe' if issues else 'safe',
                "issues": issues,
                "metadata": {
                    "file_name": file_path.name,
                    "scan_time": str(scan_end - scan_start),
                    "target": "file",
                    "summary": "Scan completed successfully"
                }
            }
            
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            return {
                "module": "StaticAnalysis",
                "file": str(file_path) if file_path else "N/A",
                "endpoint": None,
                "status": "error",
                "issues": [{
                    "type": "error",
                    "description": str(e),
                    "severity": "CRITICAL",
                    "location": "N/A"
                }],
                "metadata": {
                    "file_name": file_path.name if hasattr(file_path, 'name') else "N/A",
                    "scan_time": "N/A",
                    "target": "file",
                    "summary": f"Scan failed: {str(e)}"
                }
            }

    def scan_endpoint(self, endpoint_url: str) -> Dict:
        return {
            "module": "StaticAnalysis",
            "file": None,
            "endpoint": endpoint_url,
            "status": "error",
            "issues": [{
                "type": "error",
                "description": "Endpoint scanning not supported by ModelScan",
                "severity": "CRITICAL",
                "location": "N/A"
            }],
            "metadata": {
                "file_name": "N/A",
                "scan_time": "N/A",
                "target": "endpoint",
                "summary": "Endpoint scanning not supported"
            }
        }

    @property
    def supported_formats(self) -> List[str]:
        return [
            ".pkl", ".pickle",    # Pickle formats
            ".h5", ".hdf5",       # HDF5 formats
            ".pb",                # TensorFlow SavedModel
            ".keras",             # Keras v3 format
            ".onnx",             # ONNX format
            ".pt", ".pth",       # PyTorch formats
            ".joblib"            # scikit-learn joblib format
        ]
