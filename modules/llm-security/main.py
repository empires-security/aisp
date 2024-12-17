import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from scanner import LLMSecurityScanner
from garak import __description__ as garak_description
from garak import _config as garak_config

def setup_logging():
    # Reset logging handlers to avoid conflicts
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get the module-specific logger and explicitly set its level
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger

def parse_args():
    parser = argparse.ArgumentParser(description='LLM Security Testing Module (powered by Garak)')
    
    # Required arguments matching AISP pattern
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='Path to the model file to scan')
    group.add_argument('--endpoint', help='URL of the model endpoint to scan')
    
    parser.add_argument('--framework', required=True,
                      choices=['openai', 'anthropic', 'huggingface', 'custom'],
                      help='LLM framework/provider being tested')
    parser.add_argument('--model-name', required=True,
                      help='Name/ID of the model (e.g., gpt-4, claude-2, custom)')
    
    # Garak-specific options
    parser.add_argument('--probe-suites', nargs='+', 
                      default=['injection', 'xss', 'prompt_leak'],
                      help='Garak probe suites to run')
    parser.add_argument('--detector-suites', nargs='+',
                      help='Specific Garak detectors to use')
    parser.add_argument('--buff-suites', nargs='+',
                      help='Garak buffs/fuzzing techniques to apply')
    
    # API Configuration
    parser.add_argument('--api-key', help='API key for the LLM service')
    parser.add_argument('--request-format', help='Request format template')
    parser.add_argument('--response-key', help='Key to extract predictions from response')
    parser.add_argument('--headers', type=json.loads, help='HTTP headers as JSON')
    
    # Output options
    parser.add_argument('--output', choices=['json', 'text'], default='json',
                      help='Output format (default: json)')
    parser.add_argument('--output-file', help='Write output to file instead of stdout')
    
    return parser.parse_args()

def format_text_output(data):
    """Format JSON output as human-readable text."""
    text = f"""=== LLM Security Test Report ===
Timestamp: {datetime.now().isoformat()}Z
Module: {data['module']}
Framework: {data['metadata']['framework']}
Model: {data['metadata']['model_name']}
{'File: ' + data['file'] if data['file'] else 'Endpoint: ' + data['endpoint']}
Status: {data['status'].upper()}
Garak Version: {data['metadata']['garak_version']}

Summary: {data['metadata']['summary']}

Test Configuration:
- Probe Suites: {', '.join(data['metadata']['test_details']['probe_suites'])}
- Detector Suites: {', '.join(data['metadata']['test_details']['detector_suites'] or ['none'])}
- Buff Suites: {', '.join(data['metadata']['test_details']['buff_suites'] or ['none'])}
- Total Probes: {data['metadata']['test_details']['total_probes']}
- Completed Tests: {data['metadata']['test_details']['completed_tests']}
- Failed Tests: {data['metadata']['test_details']['failed_tests']}

Errors:"""

    if data['metadata']['test_details']['error_details']:
        for error in data['metadata']['test_details']['error_details']:
            text += f"\n- {error['error_type']}: {error['error_message']}"
            if 'probe' in error:
                text += f" (in probe: {error['probe']})"
    else:
        text += "\nNone"

    if data['issues']:
        text += "\n\nVulnerabilities Found:\n"
        for issue in data['issues']:
            text += f"\n[{issue['type'].upper()}] {issue['description']}\n"
            text += f"Severity: {issue['severity']}\n"
            text += f"Attack Type: {issue['attack_type']}\n"
            if 'attack_details' in issue:
                text += f"Details: {issue['attack_details']}\n"
    else:
        text += "\n\nNo vulnerabilities found."
    
    text += f"\nTest Details:\n"
    text += f"- Completed Probes: {', '.join(data['metadata']['test_details']['completed_probes']) or 'none'}\n"
    text += f"- Failed Probes: {', '.join(data['metadata']['test_details']['failed_probes']) or 'none'}\n"
    text += f"- Skipped Probes: {', '.join(data['metadata']['test_details']['skipped_probes']) or 'none'}"
    
    return text

def main():
    logger = setup_logging()
    args = parse_args()
    
    try:
        scanner = LLMSecurityScanner(
            model_path=args.file,
            endpoint=args.endpoint,
            framework=args.framework,
            model_name=args.model_name,
            api_key=args.api_key,
            probe_suites=args.probe_suites,
            detector_suites=args.detector_suites,
            buff_suites=args.buff_suites,
            request_format=args.request_format,
            response_key=args.response_key,
            headers=args.headers
        )
        
        results = scanner.run_tests()
        
        if args.output == 'text':
            output = format_text_output(results)
        else:
            output = json.dumps(results, indent=4)
            
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
        else:
            print(output)
                
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        raise

if __name__ == '__main__':
    main()