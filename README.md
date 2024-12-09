# AI Secure Pipeline

A modular and comprehensive framework to safeguard AI models and inference endpoints against emerging threats, integrating seamlessly into DevSecOps pipelines like Jenkins, GitHub Actions, and SonarQube. 

## Features
- **Static Model Analysis**: Detect unsafe code or malicious payloads in serialized AI model files (e.g., Pickle, H5).
- **Adversarial Robustness Testing**: Evaluate AI models against adversarial attacks to identify vulnerabilities and improve resilience.
- **LLM Specific Security**: Address vulnerabilities unique to Large Language Models (LLMs), such as prompt leaking, adversarial robustness, and memory attacks.
- **NLP Model Security**: Perform adversarial testing and data augmentation for Natural Language Processing (NLP) systems.
- **Multimodal Robustness Testing**: Assess AI model performance across multiple data types, including text, images, audio, and video.
- **Supply Chain Integrity**: Monitor and validate the integrity of AI/ML artifacts throughout the CI/CD pipeline.
- **Deployment Monitoring**: Provide real-time monitoring for inference endpoints to detect security threats and anomalies.

## Modules Overview

The pipeline integrates best-in-class tools to secure AI systems, categorized into modular components:

**1. Static Model Analysis**
  - Scans serialized models for unsafe practices, vulnerabilities, including malicious payloads in Pickle or H5 files.
  - Tools: [Protect AI's ModelScan](https://github.com/protectai/modelscan)

**2. Adversarial Robustness Testing**
  - Tests model robustness against adversarial inputs.
  - Simulates evasion, poisoning, and extraction attacks to evaluate model vulnerabilities.
  - Supports adversarial testing for classification and regression models across major ML frameworks.
  - Tools: [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)

**3. LLM Specific Security**
  - Probes vulnerabilities unique to LLMs, including prompt leaking, multimodal attacks and adversarial input handling.
  - Tools: [NVIDIA Garak](https://github.com/NVIDIA/garak)

**4. NLP Model Security**
  - Conducts adversarial testing for NLP systems to ensure robustness.
  - Provides advanced data augmentation to improve training datasets.
  - Facilitates adversarial training to strengthen model security.
  - Tools: [TextAttack](https://github.com/QData/TextAttack)

**5. Multimodal Robustness Testing**
  - Applies data augmentations across text, images, audio, and video to simulate real-world variability.
  - Tests model robustness under diverse and adversarial conditions.
  - Tools: [AugLy](https://github.com/facebookresearch/AugLy)

**6. Supply Chain Integrity**
  - Tracks and validates the integrity of training artifacts in the ML supply chain.
  - Detects risks and provides actionable insights for secure development pipelines.
  - Tools: [AIShield Watchtower](https://github.com/bosch-aisecurity-aishield/watchtower)

**7. Deployment Monitoring**
  - Continuously monitors inference endpoints for security threats.
  - Detects anomalies and provides alerts for real-time response.
  - Tools: [HiddenLayer Model Scanner](https://hiddenlayer.com/model-scanner/)

## Installation

### Prerequisites
- Docker
- Python 3.9+
- AWS CLI (for deploying to Amazon SageMaker)

### Clone the Repository
```bash
git clone https://github.com/empires-security/aisp.git
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
python modules/static-analysis/main.py --file path/to/model.pickle [--output json|text]
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
name: AI Secure Pipeline

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

## Attributions

This project leverages the following open-source tools:
- **[Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)**
- **[TextAttack](https://github.com/QData/TextAttack)**
- **[AugLy](https://github.com/facebookresearch/AugLy)**
- **[Protect AI's ModelScan](https://github.com/protectai/modelscan)**
- **[NVIDIA Garak](https://github.com/NVIDIA/garak)**
- **[AIShield Watchtower](https://github.com/bosch-aisecurity-aishield/watchtower)**

## Contributing
We welcome contributions! Please see our CONTRIBUTING.md for guidelines on submitting issues, feature requests, or pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

