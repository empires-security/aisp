import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from io import StringIO
from pathlib import Path
from main import setup_argparser, format_text_output, write_output, main, list_supported_formats

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_result = {
            "module": "StaticAnalysis",
            "file": "model.pt",
            "endpoint": None,
            "status": "unsafe",
            "issues": [
                {
                    "type": "vulnerability",
                    "description": "Unprotected model weights",
                    "severity": "HIGH",
                    "location": "weights.h5"
                }
            ],
            "metadata": {
                "summary": "Security issues detected",
                "scan_time": "1.23s"
            }
        }
        # Create a temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory and its contents
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_setup_argparser(self):
        """Test argument parser configuration."""
        parser = setup_argparser()
        
        # Test with file input
        args = parser.parse_args(['--file', 'model.pt'])
        self.assertEqual(args.file, 'model.pt')
        self.assertEqual(args.output, 'json')  # default value
        
        # Test with endpoint input
        args = parser.parse_args(['--endpoint', 'http://example.com'])
        self.assertEqual(args.endpoint, 'http://example.com')
        
        # Test output format selection
        args = parser.parse_args(['--file', 'model.pt', '--output', 'text'])
        self.assertEqual(args.output, 'text')
        
        # Test verbose flag
        args = parser.parse_args(['--file', 'model.pt', '--verbose'])
        self.assertTrue(args.verbose)

    def test_format_text_output(self):
        """Test text formatting of scan results."""
        output = format_text_output(self.sample_result)
        
        self.assertIn("=== Static Analysis Scan Report ===", output)
        self.assertIn("Module: StaticAnalysis", output)
        self.assertIn("File: model.pt", output)
        self.assertIn("Status: UNSAFE", output)
        self.assertIn("Security issues detected", output)
        self.assertIn("Scan Time: 1.23s", output)
        self.assertIn("[VULNERABILITY] Unprotected model weights", output)
        self.assertIn("Severity: HIGH", output)
        self.assertIn("Location: weights.h5", output)

    def test_write_output_json(self):
        """Test JSON output writing."""
        output_buffer = StringIO()
        write_output(self.sample_result, 'json', output_buffer)
        output_content = output_buffer.getvalue()
        
        # Verify JSON output
        parsed_output = json.loads(output_content)
        self.assertEqual(parsed_output, self.sample_result)
        self.assertEqual(parsed_output['status'], 'unsafe')
        self.assertEqual(len(parsed_output['issues']), 1)

    def test_write_output_text(self):
        """Test text output writing."""
        output_buffer = StringIO()
        write_output(self.sample_result, 'text', output_buffer)
        output_content = output_buffer.getvalue()
        
        self.assertIn("Static Analysis Scan Report", output_content)
        self.assertIn("Status: UNSAFE", output_content)
        self.assertIn("Unprotected model weights", output_content)

    @patch('main.ModelScanner')
    def test_list_supported_formats(self, mock_scanner_class):
        """Test listing of supported formats."""
        mock_scanner = Mock()
        mock_scanner.supported_formats = ['pytorch', 'tensorflow', 'onnx']
        mock_scanner_class.return_value = mock_scanner
        
        # Capture stdout
        output_buffer = StringIO()
        with patch('sys.stdout', output_buffer):
            list_supported_formats(mock_scanner)
        
        output = output_buffer.getvalue()
        self.assertIn("Supported Model Formats:", output)
        self.assertIn("pytorch", output)
        self.assertIn("tensorflow", output)
        self.assertIn("onnx", output)

    @patch('main.ModelScanner')
    def test_main_exit_codes(self, mock_scanner_class):
        """Test different exit codes for various scenarios."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        
        # Test safe model (exit code 0)
        mock_scanner.scan_file.return_value = {
            "status": "safe",
            "issues": []
        }
        with patch('sys.argv', ['main.py', '--file', 'safe_model.pt']):
            self.assertEqual(main(), 0)
        
        # Test unsafe model (exit code 1)
        mock_scanner.scan_file.return_value = {
            "status": "unsafe",
            "issues": [{"type": "vulnerability"}]
        }
        with patch('sys.argv', ['main.py', '--file', 'unsafe_model.pt']):
            self.assertEqual(main(), 1)
        
        # Test error case (exit code 2)
        mock_scanner.scan_file.return_value = {
            "status": "error",
            "issues": [{"type": "error"}]
        }
        with patch('sys.argv', ['main.py', '--file', 'error_model.pt']):
            self.assertEqual(main(), 2)

    @patch('main.ModelScanner')
    def test_main_with_file_output(self, mock_scanner_class):
        """Test main function with file output."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.scan_file.return_value = {
            "status": "safe",
            "issues": []
        }
        
        output_file = os.path.join(self.temp_dir, 'output.json')
        with patch('sys.argv', ['main.py', '--file', 'model.pt', '--output-file', output_file]):
            with patch('argparse.FileType', mock_open()):
                self.assertEqual(main(), 0)

    @patch('main.ModelScanner')
    def test_main_error_handling(self, mock_scanner_class):
        """Test error handling in main function."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.scan_file.side_effect = Exception("Test error")
        
        with patch('sys.argv', ['main.py', '--file', 'model.pt']):
            self.assertEqual(main(), 2)

    @patch('main.ModelScanner')
    def test_main_verbose_logging(self, mock_scanner_class):
        """Test verbose logging configuration."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.scan_file.return_value = {"status": "safe", "issues": []}
        
        with patch('sys.argv', ['main.py', '--file', 'model.pt', '--verbose']):
            with patch('logging.getLogger') as mock_logger:
                main()
                mock_logger.return_value.setLevel.assert_called_once()

if __name__ == '__main__':
    unittest.main()
