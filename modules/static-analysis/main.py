# main.py
import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Optional, Union, TextIO
from datetime import datetime
from scanner import ModelScanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparser() -> argparse.ArgumentParser:
    """Configure command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Static Analysis Scanner for AI Models',
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
        help='URL of the model endpoint to scan (currently unsupported)'
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
    
    # List supported formats
    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='List supported model formats and exit'
    )
    
    return parser

def format_text_output(result: dict) -> str:
    """
    Format scan results as human-readable text.
    
    Args:
        result: Scan results dictionary
        
    Returns:
        str: Formatted text output
    """
    output = []
    output.append("=== Static Analysis Scan Report ===")
    output.append(f"Timestamp: {datetime.now().isoformat()}")
    output.append(f"Module: {result['module']}")
    
    if result['file']:
        output.append(f"File: {result['file']}")
    if result['endpoint']:
        output.append(f"Endpoint: {result['endpoint']}")
        
    output.append(f"Status: {result['status'].upper()}")
    
    # Add summary if available
    if 'metadata' in result and 'summary' in result['metadata']:
        output.append(f"\nSummary: {result['metadata']['summary']}")
    
    # Add scan time if available
    if 'metadata' in result and 'scan_time' in result['metadata']:
        output.append(f"Scan Time: {result['metadata']['scan_time']}")
    
    # List issues if any
    if result['issues']:
        output.append("\nIssues Found:")
        for issue in result['issues']:
            output.append(f"\n[{issue['type'].upper()}] {issue['description']}")
            output.append(f"Severity: {issue['severity']}")
            if issue['location'] != 'N/A':
                output.append(f"Location: {issue['location']}")
    else:
        output.append("\nNo issues detected.")
        
    return "\n".join(output)

def write_output(
    result: dict,
    output_format: str,
    output_file: Optional[TextIO] = None
) -> None:
    """
    Write scan results to specified output destination.
    
    Args:
        result: Scan results dictionary
        output_format: Format to write ('json' or 'text')
        output_file: Optional file handle to write to
    """
    if output_format == 'json':
        output_content = json.dumps(result, indent=4)
    else:
        output_content = format_text_output(result)
    
    if output_file:
        output_file.write(output_content)
        output_file.write('\n')
    else:
        print(output_content)

def list_supported_formats(scanner: ModelScanner) -> None:
    """Display supported model formats."""
    print("\nSupported Model Formats:")
    for fmt in scanner.supported_formats:
        print(f"  - {fmt}")
    print("\nNote: Format support is provided by ModelScan library.")

def main() -> int:
    """
    Main entry point for the static analysis scanner.
    
    Returns:
        int: Exit code (0: success, 1: issues found, 2: error)
    """
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = ModelScanner()
    
    # Handle format listing
    if args.list_formats:
        list_supported_formats(scanner)
        return 0
    
    try:
        # Perform scan based on input type
        if args.file:
            logger.info(f"Scanning file: {args.file}")
            result = scanner.scan_file(args.file)
        else:
            logger.info(f"Scanning endpoint: {args.endpoint}")
            result = scanner.scan_endpoint(args.endpoint)
        
        # Write output
        write_output(result, args.output, args.output_file)
        
        # Determine exit code based on scan result
        if result['status'] == 'error':
            return 2
        elif result['status'] == 'unsafe':
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=args.verbose)
        error_result = {
            "module": "StaticAnalysis",
            "file": args.file,
            "endpoint": args.endpoint,
            "status": "error",
            "issues": [{
                "type": "error",
                "description": str(e),
                "severity": "CRITICAL",
                "location": "N/A"
            }],
            "metadata": {
                "file_name": Path(args.file).name if args.file else "N/A",
                "scan_time": "N/A",
                "target": "file" if args.file else "endpoint",
                "summary": f"Fatal error: {str(e)}"
            }
        }
        write_output(error_result, args.output, args.output_file)
        return 2

if __name__ == '__main__':
    sys.exit(main())
