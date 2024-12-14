# Integration Guide for Adversarial Testing Module

## Overview
This guide provides detailed instructions for integrating the Adversarial Testing module into various CI/CD pipelines and development workflows.

## Table of Contents
- [GitHub Actions Integration](#github-actions-integration)
- [Jenkins Pipeline Integration](#jenkins-pipeline-integration)
- [GitLab CI Integration](#gitlab-ci-integration)
- [SonarQube Integration](#sonarqube-integration)
- [Azure DevOps Integration](#azure-devops-integration)
- [Docker Integration](#docker-integration)

## GitHub Actions Integration

### Basic Integration
```yaml
name: AI Security Scan
on: [push, pull_request]

jobs:
  adversarial-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r modules/adversarial-testing/requirements.txt
          
      - name: Prepare test data
        run: |
          python scripts/generate_test_data.py \
            --samples 1000 \
            --output test_samples.npz
          
      - name: Run adversarial testing
        run: |
          python modules/adversarial-testing/main.py \
            --file models/classifier.h5 \
            --framework tensorflow \
            --test-data test_samples.npz \
            --output json \
            --output-file scan_results.json
            
      - name: Upload scan results
        uses: actions/upload-artifact@v2
        with:
          name: adversarial-scan-results
          path: scan_results.json
```

### Advanced Configuration
```yaml
name: AI Security Scan (Advanced)
on:
  push:
    paths:
      - 'models/**'
      - 'modules/adversarial-testing/**'
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  adversarial-testing:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        framework: [tensorflow, pytorch, sklearn]
        
    steps:
      # ... (basic steps) ...
      
      - name: Run adversarial testing
        run: |
          python modules/adversarial-testing/main.py \
            --file models/${{ matrix.framework }}_model \
            --framework ${{ matrix.framework }} \
            --test-data test_samples.npz
            
      - name: Report status
        if: always()
        uses: actions/github-script@v3
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('scan_results.json', 'utf8'));
            const issueBody = `Adversarial testing found ${results.issues.length} issues`;
            github.issues.create({
              ...context.repo,
              title: 'Adversarial Testing Results',
              body: issueBody
            });
```

## Jenkins Pipeline Integration

### Basic Pipeline
```groovy
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        MODEL_PATH = 'models/classifier.h5'
        TEST_DATA = 'data/test_samples.npz'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r modules/adversarial-testing/requirements.txt
                '''
            }
        }
        
        stage('Prepare Test Data') {
            steps {
                sh 'python scripts/generate_test_data.py --samples 1000 --output ${TEST_DATA}'
            }
        }
        
        stage('Adversarial Testing') {
            steps {
                script {
                    def scanResult = sh(
                        script: """
                            python modules/adversarial-testing/main.py \
                                --file ${MODEL_PATH} \
                                --framework tensorflow \
                                --test-data ${TEST_DATA} \
                                --output json \
                                --output-file scan_results.json
                        """,
                        returnStatus: true
                    )
                    
                    if (scanResult == 2) {
                        error('Adversarial testing failed')
                    } else if (scanResult == 1) {
                        unstable('Vulnerabilities detected')
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'scan_results.json'
                junit '**/test-results/*.xml'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

## GitLab CI Integration

```yaml
adversarial_testing:
  image: python:3.9
  script:
    - pip install -r modules/adversarial-testing/requirements.txt
    - python scripts/generate_test_data.py --samples 1000 --output test_samples.npz
    - |
      python modules/adversarial-testing/main.py \
        --file model.h5 \
        --framework tensorflow \
        --test-data test_samples.npz \
        --output json \
        --output-file scan_results.json
  artifacts:
    paths:
      - scan_results.json
    reports:
      junit: test-results/test-report.xml
```

## SonarQube Integration

### sonar-project.properties
```properties
sonar.projectKey=aisp-adversarial
sonar.projectName=AI Security Pipeline - Adversarial Testing
sonar.sources=modules/adversarial-testing
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results/test-report.xml
sonar.python.pylint.reportPath=pylint-report.txt
```

### Integration Script
```bash
#!/bin/bash
# Run tests with coverage
coverage run -m pytest
coverage xml

# Run pylint
pylint modules/adversarial-testing > pylint-report.txt

# Run sonar-scanner
sonar-scanner \
  -Dsonar.projectKey=aisp-adversarial \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=your-token
```

## Azure DevOps Integration

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'
    
- script: |
    python -m pip install --upgrade pip
    pip install -r modules/adversarial-testing/requirements.txt
  displayName: 'Install dependencies'
  
- script: |
    python scripts/generate_test_data.py --samples 1000 --output test_samples.npz
  displayName: 'Generate test data'
  
- script: |
    python modules/adversarial-testing/main.py \
      --file $(MODEL_PATH) \
      --framework tensorflow \
      --test-data test_samples.npz \
      --output json \
      --output-file $(Build.ArtifactStagingDirectory)/scan_results.json
  displayName: 'Run adversarial testing'
  
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'ScanResults'
```

## Docker Integration

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy module files
COPY modules/adversarial-testing /app/adversarial-testing
COPY scripts/generate_test_data.py /app/scripts/

# Set entrypoint
ENTRYPOINT ["python", "/app/adversarial-testing/main.py"]
```

### Docker Compose
```yaml
version: '3'
services:
  adversarial-testing:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    command: [
      "--file", "/app/models/classifier.h5",
      "--framework", "tensorflow",
      "--test-data", "/app/data/test_samples.npz"
    ]
```

## Best Practices

### Integration Guidelines
1. Always pin dependency versions
2. Use environment variables for sensitive information
3. Implement proper error handling
4. Archive test results and artifacts
5. Set up notifications for failures
6. Implement proper timeout handling

### Security Considerations
1. Secure storage of model files
2. Protected test data handling
3. Proper credential management
4. Network security for endpoint testing
5. Resource limitation implementation

### Performance Optimization
1. Cache dependencies
2. Use parallel testing when possible
3. Implement test data reuse
4. Configure appropriate timeouts
5. Optimize resource allocation

