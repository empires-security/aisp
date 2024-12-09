import argparse
import json
from scanner import run_modelscan

def standardize_output(file_name, results):
    """
    Standardize the output format for ModelScan results.
    Args:
        file_name (str): Name of the scanned file.
        results (dict): Raw results from ModelScan.
    Returns:
        dict: Standardized output.
    """
    standardized_results = {
        "module": "StaticAnalysis",
        "file": file_name,
        "status": "safe" if len(results.get("issues", [])) == 0 else "unsafe",
        "issues": results.get("issues", []),
        "metadata": {
            "file_name": results.get("input_path", file_name),
            "scan_time": results.get("scan_time", "N/A"),
        }
    }
    return standardized_results

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Run StaticAnalysis on a serialized AI model file.")
    parser.add_argument("--file", required=True, help="Path to the model file (e.g., Pickle, H5).")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format (json or text).")
    args = parser.parse_args()

    try:
        # Run the scan
        raw_results = run_modelscan(args.file)

        # Standardize the output
        standardized_results = standardize_output(args.file, raw_results)

        # Display results
        if args.output == "json":
            print(json.dumps(standardized_results, indent=4))
        else:
            print(f"Module: {standardized_results['module']}")
            print(f"File: {standardized_results['file']}")
            print(f"Status: {standardized_results['status']}")
            if standardized_results["issues"]:
                print("Issues Detected:")
                for issue in standardized_results["issues"]:
                    print(f"  - Type: {issue['severity']}, Description: {issue['description']}")
            else:
                print("No issues detected.")

    except Exception as e:
        print(json.dumps({
            "module": "StaticAnalysis",
            "file": args.file,
            "status": "error",
            "error_message": str(e)
        }, indent=4))

if __name__ == "__main__":
    main()
