# LLM Security Testing Module

## Overview
The LLM Security Testing Module is a critical component of the AI Secure Pipeline (AISP) that evaluates Large Language Models (LLMs) against various security vulnerabilities and attack vectors. Built on top of NVIDIA's Garak framework, it provides comprehensive testing for:

- Prompt injection attacks
- Cross-site scripting (XSS) attempts
- Data leakage vulnerabilities
- Memory manipulation attacks
- Output manipulation
- Malicious prompt crafting

## Features

### Framework Support
- OpenAI API (.openai)
- Anthropic API (.anthropic)
- Hugging Face Models (.h5, .bin)
- Custom REST API endpoints

### Attack Types
- **Prompt Injection**
  - Direct injection
  - Indirect command injection
  - Context leakage
- **Data Extraction**
  - Training data extraction
  - Parameter extraction
  - Configuration leakage
- **Malicious Output**
  - XSS payloads
  - Code injection
  - Command injection

### Output Features
- JSON output (machine-readable)
- Text output (human-readable)
- File output support
- Detailed vulnerability metrics
- Attack success rates and severity levels

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- Virtual environment (recommended)
- GPU support (optional, for local models)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/empires-security/aisp.git
cd aisp/modules/llm-security
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Test an OpenAI model
python main.py --framework openai \
              --model-name gpt-4 \
              --api-key YOUR_API_KEY \
              --probe-suites injection prompt_leak

# Test a local Hugging Face model
python main.py --file path/to/model \
              --framework huggingface \
              --model-name local-llm \
              --probe-suites injection xss

# Test a custom endpoint
python main.py --endpoint https://api.example.com/generate \
              --framework custom \
              --model-name custom-llm \
              --request-format "prompt=<input>,max_tokens=100" \
              --response-key "completion"
```

#### Command Line Options

Required arguments:
```
  --file PATH              Path to the model file to scan
  --endpoint URL           URL of the model endpoint to scan
  --framework             Framework used (openai, anthropic, huggingface, custom)
  --model-name           Name/ID of the model to test
```

Optional arguments:
```
  --probe-suites         List of probe suites to run
  --detector-suites      List of detectors to use
  --buff-suites          List of buffs/fuzzing techniques to apply
  --generations          Number of generations per prompt (default: 5)
  --eval-threshold       Minimum threshold for success (default: 0.5)
  --parallel-requests    Number of parallel requests (default: 1)
  --api-key              API key for the service
  --request-format       Request format for custom endpoints
  --response-key         Response key for custom endpoints
  --headers              HTTP headers as JSON
  --output               Output format (json/text)
  --output-file          Write output to file
```

### Output Format

#### JSON Output Structure
```json
{
    "module": "LLMSecurityTesting",
    "file": "path/to/model",
    "endpoint": null,
    "status": "unsafe",
    "issues": [
        {
            "type": "error",
            "description": "Successful prompt injection attack",
            "severity": "HIGH",
            "attack_type": "injection",
            "attack_name": "system_prompt_leak",
            "attack_details": {
                "prompt": "...",
                "response": "...",
                "success_rate": 0.8,
                "probe": "prompt_injection",
                "detector": "basic"
            }
        }
    ],
    "metadata": {
        "scan_time": "0:05:30.123456",
        "target": "file",
        "framework": "huggingface",
        "model_name": "local-llm",
        "garak_version": "0.9.1",
        "test_details": {
            "completed_tests": 50,
            "failed_tests": 2,
            "probe_suites": ["injection", "xss"],
            "detector_suites": ["basic"],
            "buff_suites": [],
            "generations": 5,
            "eval_threshold": 0.5
        },
        "summary": "Found 1 issue in 50 tests"
    }
}
```

## Integration
For detailed integration instructions with various CI/CD platforms and LLM deployments, see [INTEGRATIONS.md](INTEGRATIONS.md).

## Development

### Project Structure
```
llm-security/
├── main.py              # CLI entry point
├── scanner.py           # Core testing logic
├── tests/               # Test files
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_main.py
├── requirements.txt    # Python dependencies
├── README.md           # Module documentation
└── INTEGRATIONS.md     # Integration guides
```

### Running Tests
```bash
# Run all tests
python -m unittest discover -s tests

# Run with coverage
coverage run -m unittest discover
coverage report
```

