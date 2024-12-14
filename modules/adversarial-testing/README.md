# Adversarial Testing Module

## Overview
The Adversarial Testing Module is a critical component of the AI Secure Pipeline (AISP) that evaluates AI models against various adversarial attacks. It uses the Adversarial Robustness Toolbox (ART) to simulate different attack vectors and assess model vulnerabilities.

## Features

### Framework Support
- **TensorFlow/Keras** (.h5, SavedModel)
- **PyTorch** (.pt, .pth)
- **scikit-learn** (.joblib, .pkl)
- **REST API Endpoints**

### Attack Types
#### Evasion Attacks
- Fast Gradient Sign Method (FGSM)
- Projected Gradient Descent (PGD)
- Carlini & Wagner L2
- DeepFool

#### Extraction Attacks
- Copycat CNN
- Knockoff Nets

#### Poisoning Attacks
- Backdoor Attacks
- SVM Attacks

### Output Features
- JSON output (machine-readable)
- Text output (human-readable)
- File output support
- Detailed vulnerability metrics

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- (Optional) CUDA support for GPU acceleration

### Setup
1. Clone the repository:
```bash
git clone https://github.com/empires-security/aisp.git
cd aisp/modules/adversarial-testing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Test a file-based model
python main.py --file model.h5 --framework tensorflow --test-data test_samples.npz

# Test a REST endpoint
python main.py --endpoint https://api.example.com/generate \
              --framework tensorflow \
              --test-data test_samples.npz \
              --input-shape 1,28,28,1 \
              --num-classes 10 \
              --request-format "prompt=<input>,max_tokens=100" \
              --response-key "completion"
              --output json
```

#### Command Line Options
```plaintext
Required arguments:
  --file PATH              Path to the model file to scan
  --endpoint URL           URL of the model endpoint to scan
  --framework {tensorflow,pytorch,sklearn}
                           ML framework used for the model
  --test-data PATH         Path to test data file (numpy .npz format)
  --request-format         Request format as key=value pairs (e.g., prompt=<input>,max_tokens=100) or JSON
  --response-key           Key to extract predictions from response

Optional arguments:
  --input-shape SHAPE      Input shape for endpoint testing (comma-separated)
  --num-classes NUM        Number of classes for endpoint testing
  --headers                JSON object of HTTP headers, e.g. Authorization, X-API-KEY
  --output {json,text}     Output format (default: json)
  --output-file FILE       Write output to file instead of stdout
```

## Output Format

### JSON Output Structure
```json
{
    "module": "AdversarialTesting",
    "file": "path/to/model.h5",
    "endpoint": null,
    "status": "unsafe",
    "issues": [
        {
            "type": "error",
            "description": "Model vulnerable to FGSM attack (success rate: 45.2%)",
            "severity": "HIGH",
            "attack_type": "evasion",
            "attack_name": "fgsm"
        },
        {
            "type": "warning",
            "description": "Model shows moderate vulnerability to PGD attack (success rate: 28.5%)",
            "severity": "MEDIUM",
            "attack_type": "evasion",
            "attack_name": "pgd"
        }
    ],
    "metadata": {
        "scan_time": "0:00:30.123456",
        "target": "file",
        "framework": "tensorflow",
        "test_samples": 1000,
         "test_details": {
            "evasion_tests": 4,
            "extraction_tests": 2,
            "poisoning_tests": 2,
            "completed_tests": 8,
            "failed_tests": 2
        },
        "summary": "Found 2 issues in 8 tests"
    }
}
```

### Text Output Format
```plaintext
=== Adversarial Robustness Test Report ===
Timestamp: 2024-12-12T10:30:00.000Z
Module: AdversarialTesting
Framework: tensorflow
File: path/to/model.h5
Test Samples: 1000
Status: UNSAFE
Scan Time: 0:00:30.123456

Summary: Found 2 issues in 8 tests

Vulnerabilities Found:

[ERROR] Model vulnerable to FGSM attack (success rate: 45.2%)
Severity: HIGH
Attack Type: evasion

[WARNING] Model shows moderate vulnerability to PGD attack (success rate: 28.5%)
Severity: MEDIUM
Attack Type: evasion

Test Details:
- Evasion Tests: 4 completed
- Extraction Tests: 2 completed
- Poisoning Tests: 2 completed
```

## Integration

For detailed integration instructions with various CI/CD platforms and tools, see [INTEGRATIONS.md](INTEGRATIONS.md).

## Development

### Project Structure
```plaintext
adversarial-testing/
├── main.py               # CLI entry point
├── scanner.py            # Core testing logic
├── scripts/              # Scripts to create test models and data
├── tests/                # Test files
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_main.py
├── requirements.txt      # Python dependencies
└── README.md             # Module documentation
```

### Testing

#### Running Tests
```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test category
python -m unittest tests.test_attacks

# Run with coverage
coverage run -m unittest discover
coverage report
coverage html  # Generates HTML report
```

#### Test Data Generation
```bash
# Generate test data for development
python scripts/generate_test_data.py \
    --format tensorflow \
    --samples 1000 \
    --output test_data.npz
```
