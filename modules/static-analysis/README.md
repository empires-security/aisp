# Static Analysis Module

The **Static Analysis Module** is part of the AI Secure Pipeline and focuses on scanning serialized AI model files for vulnerabilities, such as unsafe deserialization or embedded malicious payloads. It leverages **Protect AI's ModelScan** for comprehensive static analysis.

## Features

- **File Format Support**: Supports common AI model serialization formats like Pickle (`.pkl`), HDF5 (`.h5`), and TensorFlow SavedModel.
- **Vulnerability Detection**: Identifies unsafe deserialization patterns. Detects embedded malicious payloads or unsafe code.
- **Standardized Reporting**: Outputs results in both JSON (machine-readable) and text (human-readable) formats.
- **Error Handling**: Gracefully reports errors in a standardized output format.

## Installation

### Prerequisites
- Python 3.9+
- Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface (CLI)

Run the module using the provided `main.py` script:

```bash
python main.py --file <path_to_model_file> [--output json|text]
```

### Options:
- `--file`: Path to the serialized AI model file (e.g., .pkl, .h5).
- `--output`: Output format. Options:
  - `json` (default): Outputs results in a JSON format.
  - `text`: Outputs results in a human-readable text format.

## Example

### JSON Output

Command:

```bash
python main.py --file test_files/safe_model.pkl --output json
```

Output
```json
{
    "module": "StaticAnalysis",
    "file": "test_files/safe_model.pkl",
    "status": "safe",
    "issues": [],
    "metadata": {
        "file_name": "test_files/safe_model.pkl",
        "scan_time": "N/A"
    }
}
```

### Text Output

Command:
```bash
python main.py --file test_files/example_model.h5 --output text
```

Output:
```plaintext
Module: StaticAnalysis
File: test_files/safe_model.pkl
Status: safe
No issues detected.
```

## Development

### Folder Structure

```plaintext
static-analysis/
├── main.py            # Entry point for the CLI
├── scanner.py         # Core logic for invoking ModelScan
├── requirements.txt   # Python dependencies
├── test_files/        # Example model files for testing
└── tests/             # Unit tests
```

### Running Unit Tests

The module includes unit tests for key functionality. To run tests:

```bash
python -m unittest discover -s tests
```

## Output Integration

The module generates standardized outputs designed for integration into the AI Secure Pipeline. Example fields include:

- module: Identifies the scanning module (e.g., "StaticAnalysis").
- file: The scanned file path.
- status: The overall scan result (safe or unsafe).
- issues: A list of detected issues with details.
- metadata: Additional information like file_name and scan_time.

