# main.py
import argparse
import json
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Optional, TextIO
from datetime import datetime
from scanner import AdversarialScanner
from typing import Dict, List, Optional, Union, Tuple, TextIO  # Add Tuple to imports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Adversarial Robustness Testing for AI Models',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input source group (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file',
        help='Path to the model file to scan'
    )
    input_group.add_argument(
        '--endpoint',
        help='URL of the model endpoint to scan'
    )
    
    # Required test data
    parser.add_argument(
        '--test-data',
        required=True,
        help='Path to test data file (numpy .npz format)'
    )
    
    # Framework (required for file, optional for endpoint)
    parser.add_argument(
        '--framework',
        choices=['tensorflow', 'pytorch', 'sklearn'],
        help='ML framework used for the model (required for file)'
    )
    
    # Endpoint specific options
    parser.add_argument(
        '--input-shape',
        help='Input shape for endpoint testing (comma-separated, e.g., 28,28,1)'
    )
    parser.add_argument(
        '--num-classes',
        type=int,
        help='Number of classes for endpoint testing'
    )
    parser.add_argument(
        '--request-format',
        help='Request format as key=value pairs (e.g., prompt=<input>,max_tokens=100) or JSON'
    )
    parser.add_argument(
        '--response-key',
        help='Key to extract predictions from response'
    )
    parser.add_argument(
        '--headers',
        type=json.loads,
        help='JSON object of HTTP headers'
    )
    # Output options
    parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--output-file',
        type=argparse.FileType('w'),
        help='Write output to file instead of stdout'
    )
    # Verbosity options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser

def format_text_output(result: dict) -> str:
    """Format scan results as human-readable text."""
    output = []
    output.append("=== Adversarial Robustness Test Report ===")
    output.append(f"Timestamp: {datetime.now().isoformat()}")
    output.append(f"Module: {result['module']}")
    output.append(f"Framework: {result['metadata']['framework']}")
    
    if result['file']:
        output.append(f"File: {result['file']}")
    if result['endpoint']:
        output.append(f"Endpoint: {result['endpoint']}")
        
    output.append(f"Test Samples: {result['metadata']['test_samples']}")
    output.append(f"Status: {result['status'].upper()}")
    output.append(f"Scan Time: {result['metadata']['scan_time']}")

    if result['metadata']['summary']:
        output.append(f"\nSummary: {result['metadata']['summary']}")
    
    if result['issues']:
        output.append("\nVulnerabilities Found:")
        for issue in result['issues']:            
            output.append(f"\n[{issue['type'].upper()}] {issue['description']}")
            output.append(f"Severity: {issue['severity']}")
            output.append(f"Attack Type: {issue['attack_type']}")
    else:
        output.append("\nNo vulnerabilities detected.")
        
    
    return "\n".join(output)

def write_output(result: dict, output_format: str, output_file: Optional[TextIO] = None) -> None:
    """Write scan results to specified output destination."""
    if output_format == 'json':
        output_content = json.dumps(result, indent=4)
    else:
        output_content = format_text_output(result)
    
    if output_file:
        output_file.write(output_content)
        output_file.write('\n')
    else:
        print(output_content)

def load_test_data(file_path: str) -> tuple:
    """Load test data from npz file."""
    try:
        data = np.load(file_path)
        return data['x_test'], data['y_test']
    except Exception as e:
        raise RuntimeError(f"Failed to load test data: {str(e)}")

def parse_input_shape(shape_str: str) -> Tuple:
    """Parse comma-separated input shape string into tuple."""
    try:
        return tuple(map(int, shape_str.split(',')))
    except Exception as e:
        raise ValueError(f"Invalid input shape format. Expected comma-separated integers, got: {shape_str}")

def parse_request_format(format_str: str) -> Dict:
    """Parse request format string into dictionary."""
    try:
        # Handle simple key=value format
        if not format_str.startswith('{'):
            parts = format_str.split(',')
            return {k.strip(): v.strip() for k, v in (p.split('=') for p in parts)}
        # Handle JSON format
        return json.loads(format_str)
    except Exception as e:
        raise ValueError(f"Invalid request format. Use 'key1=value1,key2=value2' or valid JSON. Error: {str(e)}")

def parse_response_key(key_str: str) -> Union[str, List[str]]:
    """Parse response key string into key or list of keys for nested responses."""
    if '.' in key_str:
        return key_str.split('.')
    return key_str

def main() -> int:
    """Main entry point for adversarial testing scanner."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        scanner = AdversarialScanner()
        
        # Load test data
        x_test, y_test = load_test_data(args.test_data)
        
        # Setup scanner based on input type
        if args.file:
            if not args.framework:
                raise ValueError("--framework is required when scanning a file")
            logger.info(f"Loading model from file: {args.file}")
            scanner.load_model(args.file, args.framework)
        else:
            logger.info(f"Setting up endpoint: {args.endpoint}")
            
            # Validate required endpoint parameters
            if args.input_shape is None:
                raise ValueError("--input-shape is required for endpoint testing")
            if args.num_classes is None:
                raise ValueError("--num-classes is required for endpoint testing")
                
            # Setup endpoint with all optional parameters
            scanner.setup_endpoint(
                endpoint_url=args.endpoint,
                input_shape=parse_input_shape(args.input_shape),
                nb_classes=args.num_classes,
                request_format=parse_request_format(args.request_format) if args.request_format else None,
                response_key=parse_response_key(args.response_key) if args.response_key else None,
                headers=args.headers
            )
        
        # Run scan
        result = scanner.scan_model(x_test, y_test)
        
        # Write output
        write_output(result, args.output, args.output_file)
        
        # Determine exit code
        if result['status'] == 'error':
            return 2
        elif result['status'] == 'unsafe':
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=args.verbose)
        error_result = {
            "module": "AdversarialTesting",
            "file": args.file,
            "endpoint": args.endpoint,
            "status": "error",
            "issues": [{
                "type": "error",
                "description": str(e),
                "severity": "CRITICAL",
                "attack_type": "setup"
            }],
            "metadata": {
                "scan_time": "N/A",
                "target": "file" if args.file else "endpoint",
                "test_details": {
                    "evasion_tests": 0,
                    "extraction_tests": 0,
                    "poisoning_tests": 0,
                    "completed_tests": 0,
                    "failed_tests": 1
                },
                "summary": f"Fatal error: {str(e)}"
            }
        }
        write_output(error_result, args.output, args.output_file)
        return 2

if __name__ == '__main__':
    sys.exit(main())
