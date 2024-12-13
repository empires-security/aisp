# Static Analysis Module

## Overview
The Static Analysis Module is a core component of the AI Secure Pipeline (AISP) that performs comprehensive security scanning of AI model files. It integrates Protect AI's ModelScan to detect potential security vulnerabilities, unsafe patterns, and malicious payloads in serialized AI models.

## Features

### Model Format Support
- **Pickle Formats**: .pkl, .pickle
- **HDF5 Formats**: .h5, .hdf5
- **TensorFlow**: SavedModel (.pb)
- **Keras**: V3 format (.keras)
- **ONNX**: .onnx
- **PyTorch**: .pt, .pth
- **scikit-learn**: .joblib

### Security Checks
- Unsafe deserialization patterns
- Embedded malicious code
- Code injection vulnerabilities
- Unsafe module imports
- Known vulnerable dependencies

### Output Features
- JSON output (machine-readable)
- Text output (human-readable)
- File output support
- Detailed scan metadata

### Security Classifications
Issues are classified into severity levels:
- **CRITICAL**: Immediate security risk
- **HIGH**: Significant security concern
- **MEDIUM**: Moderate security risk
- **LOW**: Minor security consideration

## Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/empires-security/aisp.git
cd aisp/modules/static-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Scan a model file (default JSON output)
python main.py --file path/to/model.pkl

# Scan with text output
python main.py --file path/to/model.h5 --output text

# Save output to file
python main.py --file path/to/model.pkl --output-file report.json

# Enable verbose logging
python main.py --file path/to/model.pkl --verbose

# List supported formats
python main.py --list-formats
```

#### Command Line Options
```
--file PATH             Path to the model file to scan
--endpoint URL          URL of the model endpoint (currently unsupported)
--output {json,text}    Output format (default: json)
--output-file FILE      Write output to file instead of stdout
-v, --verbose          Enable verbose output
--list-formats         List supported model formats and exit
```

### Exit Codes
- `0`: Scan completed successfully, no issues found
- `1`: Scan completed successfully, issues found
- `2`: Scan failed due to error

## Output Format

### JSON Output Example
```json
{
    "module": "StaticAnalysis",
    "file": "path/to/model.pkl",
    "endpoint": null,
    "status": "unsafe",
    "issues": [
        {
            "type": "error",
            "description": "Unsafe module import detected",
            "severity": "CRITICAL",
            "location": "model.pkl:line_10"
        }
    ],
    "metadata": {
        "file_name": "model.pkl",
        "scan_time": "0:00:01.234567",
        "target": "file",
        "summary": "Found 1 issue (Critical: 1, High: 0, Medium: 0, Low: 0)"
    }
}
```

### Text Output Example
```plaintext
=== Static Analysis Scan Report ===
Timestamp: 2024-12-12T10:30:00.000Z
Module: StaticAnalysis
File: path/to/model.pkl
Status: UNSAFE

Summary: Found 1 issue (Critical: 1, High: 0, Medium: 0, Low: 0)
Scan Time: 0:00:01.234567

Issues Found:
[ERROR] Unsafe module import detected
Severity: CRITICAL
Location: model.pkl:line_10
```

## Integration

For detailed integration instructions with various CI/CD platforms and tools, see [INTEGRATIONS.md](INTEGRATIONS.md).

## Development

### Project Structure
```
static-analysis/
├── main.py               # CLI entry point
├── scanner.py            # Core scanning logic
├── scripts/              # Scripts to create test models and data
├── tests/                # Test files
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_main.py
├── requirements.txt      # Python dependencies
└── README.md             # Module documentation
```

### Running Tests
```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_scanner
```

## Contributing
1. Ensure all tests pass before submitting changes
2. Follow PEP 8 style guidelines
3. Add tests for new functionality
4. Update documentation as needed

## Limitations
- Endpoint scanning is not currently supported
- Some model formats may require additional dependencies
- Large models may require significant memory
- Nested ZIP files are not supported

## Security Considerations
- Always scan models from untrusted sources
- Monitor scan results in CI/CD pipelines
- Regularly update dependencies
- Follow security best practices for model deployment

## Support
For issues and feature requests:
- Use the GitHub issue tracker
- Contact the maintainers
- Check the documentation

## License
This module is part of the AI Secure Pipeline (AISP) project and is licensed under the MIT License.
