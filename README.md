# AI Security Pipeline

A modular security framework for AI models and inference endpoints, integrating seamlessly into DevSecOps pipelines like Jenkins, GitHub Actions, and SonarQube. **AI Security Pipeline** provides robust tools for scanning, monitoring, and safeguarding AI models against emerging threats.

## Features

- **Static Model Analysis**: Detect unsafe code or vulnerabilities in serialized AI models.
- **Adversarial Robustness Testing**: Simulate and test adversarial attacks on inference endpoints.
- **LLM-Specific Security**: Identify vulnerabilities in Large Language Models (LLMs) such as prompt injection and memory attacks.
- **Supply Chain Security**: Monitor and validate the integrity of AI/ML artifacts in CI/CD pipelines.
- **Deployment Monitoring**: Continuous threat monitoring for deployed inference endpoints.

## Modules Overview

1. **Static Analysis**: 
   - Tool: [Protect AI's ModelScan](https://github.com/protectai/modelscan)
   - Scans model files for vulnerabilities in formats like Pickle and H5.

2. **Adversarial Testing**:
   - Tool: [Microsoft Counterfit](https://github.com/Azure/counterfit)
   - Tests model robustness against adversarial inputs.

3. **LLM Security**:
   - Tool: [NVIDIA's Garak](https://github.com/NVIDIA/garak)
   - Focuses on vulnerabilities unique to LLMs, including prompt leaking and multimodal attacks.

4. **Supply Chain Security**:
   - Tool: [AIShield Watchtower](https://github.com/bosch-aisecurity-aishield/watchtower)
   - Monitors the integrity of training artifacts.

5. **Deployment Monitoring**:
   - Tool: [HiddenLayer Model Scanner](https://hiddenlayer.com/model-scanner)
   - Provides real-time monitoring of deployed AI endpoints.

## Installation

### Prerequisites
- Docker
- Python 3.9+
- AWS CLI (for deploying to Amazon SageMaker)

### Clone the Repository
```bash
git clone https://github.com/your-org/aisp.git
cd aisp
```

### Set Up Environment
**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Build Docker containers**:
```bash
docker-compose -f containers/compose/dev-compose.yml up --build
```

## Usage

### Static Analysis
Run the static analysis module on a model file:
```bash
python modules/static-analysis/main.py --file path/to/model.pickle
```

### Adversarial Testing
Test a SageMaker endpoint for adversarial robustness:
```bash
python modules/adversarial-testing/main.py --endpoint-name <SAGEMAKER_ENDPOINT_NAME>
```

### LLM Security Testing
Probe an LLM inference endpoint for vulnerabilities:
```bash
python modules/llm-security/main.py --endpoint-url <ENDPOINT_URL>
```

## Integration into CI/CD

### GitHub Actions

Add the following to your .github/workflows/security.yml:
```yaml
name: AI Security Pipeline

on:
  push:
    branches:
      - main

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Run Static Analysis
        run: python modules/static-analysis/main.py --file path/to/model.pickle

      - name: Adversarial Testing
        run: python modules/adversarial-testing/main.py --endpoint-name <SAGEMAKER_ENDPOINT_NAME>
```

## Documentation
Detailed documentation for setup, usage, and APIs can be found in the docs/ directory.

## Contributing
We welcome contributions! Please see our CONTRIBUTING.md for guidelines on submitting issues, feature requests, or pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
