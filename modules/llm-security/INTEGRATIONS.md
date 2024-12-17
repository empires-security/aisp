# LLM Security Testing Module Integration Guide

This document provides detailed instructions for integrating the LLM Security Testing Module with various CI/CD platforms and deployment environments.

## Table of Contents
- [GitHub Actions Integration](#github-actions-integration)
- [Jenkins Pipeline Integration](#jenkins-pipeline-integration)
- [GitLab CI Integration](#gitlab-ci-integration)
- [Circle CI Integration](#circle-ci-integration)
- [Local Development Integration](#local-development-integration)
- [API Gateway Integration](#api-gateway-integration)
- [Monitoring Integration](#monitoring-integration)

## GitHub Actions Integration

### Basic Workflow
Create `.github/workflows/llm-security.yml`:

```yaml
name: LLM Security Scan

on:
  push:
    paths:
      - 'models/**'
      - 'api/**'
  pull_request:
    paths:
      - 'models/**'
      - 'api/**'

jobs:
  security_scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r modules/llm-security/requirements.txt
      
      - name: Run security scan
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python modules/llm-security/main.py \
            --endpoint ${{ secrets.API_ENDPOINT }} \
            --framework custom \
            --model-name prod-llm \
            --probe-suites injection xss prompt_leak \
            --output json \
            --output-file scan-results.json
      
      - name: Check scan results
        run: |
          if grep -q '"status": "unsafe"' scan-results.json; then
            echo "Security vulnerabilities detected!"
            exit 1
          fi
```

## Jenkins Pipeline Integration

### Jenkinsfile Example
```groovy
pipeline {
    agent any
    
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate'
                sh 'pip install -r modules/llm-security/requirements.txt'
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    python modules/llm-security/main.py \
                        --endpoint ${API_ENDPOINT} \
                        --framework custom \
                        --model-name prod-llm \
                        --probe-suites injection xss \
                        --output json \
                        --output-file scan-results.json
                '''
            }
        }
        
        stage('Evaluate Results') {
            steps {
                script {
                    def results = readJSON file: 'scan-results.json'
                    if (results.status == 'unsafe') {
                        error 'Security vulnerabilities detected!'
                    }
                }
            }
        }
    }
}
```

## GitLab CI Integration

### .gitlab-ci.yml Example
```yaml
security_scan:
  image: python:3.9
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
  script:
    - pip install -r modules/llm-security/requirements.txt
    - python modules/llm-security/main.py \
        --endpoint $API_ENDPOINT \
        --framework custom \
        --model-name prod-llm \
        --probe-suites injection xss \
        --output json \
        --output-file scan-results.json
    - |
      if grep -q '"status": "unsafe"' scan-results.json; then
        echo "Security vulnerabilities detected!"
        exit 1
      fi
  artifacts:
    paths:
      - scan-results.json
```

## Circle CI Integration

### .circleci/config.yml Example
```yaml
version: 2.1

jobs:
  security_scan:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r modules/llm-security/requirements.txt
      - run:
          name: Run security scan
          command: |
            python modules/llm-security/main.py \
              --endpoint ${API_ENDPOINT} \
              --framework custom \
              --model-name prod-llm \
              --probe-suites injection xss \
              --output json \
              --output-file scan-results.json
      - store_artifacts:
          path: scan-results.json

workflows:
  version: 2
  security:
    jobs:
      - security_scan
```

## Local Development Integration

### Pre-commit Hook
Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running LLM security scan..."
python modules/llm-security/main.py \
    --endpoint http://localhost:8000/generate \
    --framework custom \
    --model-name dev-llm \
    --probe-suites injection \
    --output json \
    --output-file scan-results.json

if grep -q '"status": "unsafe"' scan-results.json; then
    echo "Security vulnerabilities detected!"
    exit 1
fi
```

Make the hook executable:
```bash
chmod +x .git/hooks/pre-commit
```
## Monitoring Integration

### Prometheus Metrics Example
```python
from prometheus_client import Counter, Gauge, start_http_server

# Define metrics
security_scans_total = Counter('llm_security_scans_total', 
                             'Total number of security scans')
vulnerabilities_found = Counter('llm_vulnerabilities_found', 
                              'Number of vulnerabilities detected')
scan_duration = Gauge('llm_scan_duration_seconds', 
                     'Duration of security scans')

# Start metrics server
start_http_server(8000)
```

### Grafana Dashboard
Create a dashboard with panels for:
- Total scans over time
- Vulnerabilities detected
- Scan duration
- Success/failure rate
- Most common vulnerability types

## Additional Resources
- [Garak Documentation](https://github.com/NVIDIA/garak)
- [LLM Security Best Practices](https://nvd.nist.gov)
