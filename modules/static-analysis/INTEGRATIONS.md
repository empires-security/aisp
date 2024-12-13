# Integration Guide for Static Analysis Module

## Overview
This guide provides detailed instructions for integrating the Static Analysis module into various CI/CD pipelines and development workflows. The module scans AI model files for potential security vulnerabilities and malicious code.

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
name: Model Security Scan
on: [push, pull_request]

jobs:
  static-analysis:
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
          pip install -r modules/static-analysis/requirements.txt
          
      - name: Run static analysis
        run: |
          python modules/static-analysis/main.py \
            --file models/model.pkl \
            --output json \
            --output-file scan_results.json
            
      - name: Upload scan results
        uses: actions/upload-artifact@v2
        with:
          name: security-scan-results
          path: scan_results.json
```

### Advanced Configuration
```yaml
name: Model Security Scan (Advanced)
on:
  push:
    paths:
      - 'models/**'
      - 'modules/static-analysis/**'
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        model-type: ['.pkl', '.h5', '.pt', '.onnx']
        
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r modules/static-analysis/requirements.txt
          
      - name: Run static analysis
        run: |
          for model in models/*${{ matrix.model-type }}; do
            python modules/static-analysis/main.py \
              --file "$model" \
              --output json \
              --output-file "scan_results_$(basename "$model").json"
          done
            
      - name: Process results
        if: always()
        run: |
          echo "Processing scan results..."
          for result in scan_results_*.json; do
            if grep -q '"status": "unsafe"' "$result"; then
              echo "Security issues found in $result"
              exit 1
            fi
          done
          
      - name: Upload scan results
        uses: actions/upload-artifact@v2
        with:
          name: security-scan-results
          path: scan_results_*.json
```

## Jenkins Pipeline Integration

### Basic Pipeline
```groovy
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        MODELS_DIR = 'models'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r modules/static-analysis/requirements.txt
                '''
            }
        }
        
        stage('Static Analysis') {
            steps {
                script {
                    def models = findFiles(glob: "${MODELS_DIR}/**/*.{pkl,h5,pt,onnx}")
                    
                    models.each { model ->
                        def scanResult = sh(
                            script: """
                                python modules/static-analysis/main.py \
                                    --file ${model.path} \
                                    --output json \
                                    --output-file scan_results_${model.name}.json
                            """,
                            returnStatus: true
                        )
                        
                        if (scanResult == 2) {
                            error("Static analysis failed for ${model.name}")
                        } else if (scanResult == 1) {
                            unstable("Security issues found in ${model.name}")
                        }
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'scan_results_*.json'
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
static_analysis:
  image: python:3.9
  script:
    - pip install -r modules/static-analysis/requirements.txt
    - |
      for model in models/*.{pkl,h5,pt,onnx}; do
        python modules/static-analysis/main.py \
          --file "$model" \
          --output json \
          --output-file "scan_results_$(basename "$model").json"
      done
  artifacts:
    paths:
      - scan_results_*.json
```

## SonarQube Integration

### sonar-project.properties
```properties
sonar.projectKey=aisp-static-analysis
sonar.projectName=AI Security Pipeline - Static Analysis
sonar.sources=modules/static-analysis
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results/test-report.xml
```

### Integration Script
```bash
#!/bin/bash
# Run tests with coverage
coverage run -m pytest
coverage xml

# Run sonar-scanner
sonar-scanner \
  -Dsonar.projectKey=aisp-static-analysis \
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
    pip install -r modules/static-analysis/requirements.txt
  displayName: 'Install dependencies'
  
- script: |
    for model in models/*.{pkl,h5,pt,onnx}; do
      python modules/static-analysis/main.py \
        --file "$model" \
        --output json \
        --output-file "$(Build.ArtifactStagingDirectory)/scan_results_$(basename "$model").json"
    done
  displayName: 'Run static analysis'
  
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'SecurityScanResults'
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
COPY modules/static-analysis /app/static-analysis

# Set entrypoint
ENTRYPOINT ["python", "/app/static-analysis/main.py"]
```

### Docker Compose
```yaml
version: '3'
services:
  static-analysis:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./models:/app/models
      - ./results:/app/results
    command: [
      "--file", "/app/models/model.pkl",
      "--output", "json",
      "--output-file", "/app/results/scan_results.json"
    ]
```

## Best Practices

### Integration Guidelines
1. Scan models before training/deployment
2. Implement proper error handling
3. Archive scan results
4. Set up notifications for security issues
5. Regular scheduled scans
6. Version control for models

### Security Considerations
1. Secure model storage
2. Access control for scan results
3. Protected credentials
4. Network security for CI/CD
5. Resource limitations

### Performance Optimization
1. Cache dependencies
2. Parallel scanning for multiple models
3. Efficient file handling
4. Appropriate timeouts
5. Resource allocation

### Monitoring and Alerting
1. Set up alerts for critical issues
2. Monitor scan performance
3. Track security metrics
4. Regular reporting
5. Incident response planning

