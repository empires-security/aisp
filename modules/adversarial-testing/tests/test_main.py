import unittest
import argparse
from unittest.mock import patch, mock_open, MagicMock
from main import (
    setup_argparser,
    load_test_data,
    parse_input_shape,
    parse_request_format,
    parse_response_key,
    format_text_output,
    write_output,
)

class TestMain(unittest.TestCase):

    def test_setup_argparser(self):
        """Test that the argument parser is correctly set up."""
        parser = setup_argparser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        args = parser.parse_args(
            [
                '--file', 'model.pth',
                '--test-data', 'data.npz',
                '--framework', 'pytorch',
                '--output', 'text'
            ]
        )
        self.assertEqual(args.file, 'model.pth')
        self.assertEqual(args.test_data, 'data.npz')
        self.assertEqual(args.framework, 'pytorch')
        self.assertEqual(args.output, 'text')

    def test_load_test_data_success(self):
        """Test loading test data from an npz file."""
        fake_data = {
            "x_test": [1, 2, 3],
            "y_test": [0, 1, 0],
        }
        with patch("numpy.load", return_value=fake_data) as mock_load:
            x_test, y_test = load_test_data("test_data.npz")
            self.assertEqual(x_test, [1, 2, 3])
            self.assertEqual(y_test, [0, 1, 0])
            mock_load.assert_called_once_with("test_data.npz")

    def test_load_test_data_failure(self):
        """Test failure in loading test data."""
        with patch("numpy.load", side_effect=RuntimeError("Load error")):
            with self.assertRaises(RuntimeError) as context:
                load_test_data("test_data.npz")
            self.assertIn("Failed to load test data", str(context.exception))

    def test_parse_input_shape_success(self):
        """Test parsing a valid input shape string."""
        input_shape = "28,28,1"
        result = parse_input_shape(input_shape)
        self.assertEqual(result, (28, 28, 1))

    def test_parse_input_shape_failure(self):
        """Test failure in parsing an invalid input shape string."""
        with self.assertRaises(ValueError):
            parse_input_shape("invalid_shape")

    def test_parse_request_format_key_value(self):
        """Test parsing a simple key=value request format string."""
        request_format = "key1=value1,key2=value2"
        result = parse_request_format(request_format)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

    def test_parse_request_format_json(self):
        """Test parsing a JSON request format string."""
        request_format = '{"key1": "value1", "key2": "value2"}'
        result = parse_request_format(request_format)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

    def test_parse_request_format_failure(self):
        """Test failure in parsing an invalid request format string."""
        with self.assertRaises(ValueError):
            parse_request_format("invalid_format")

    def test_parse_response_key_single(self):
        """Test parsing a single response key."""
        key = "output"
        result = parse_response_key(key)
        self.assertEqual(result, "output")

    def test_parse_response_key_nested(self):
        """Test parsing a nested response key string."""
        key = "data.predictions"
        result = parse_response_key(key)
        self.assertEqual(result, ["data", "predictions"])

    def test_format_text_output(self):
        """Test formatting scan results as text."""
        result = {
            "module": "AdversarialTesting",
            "metadata": {
                "framework": "pytorch",
                "test_samples": 10,
                "scan_time": "1m",
                "summary": "Test summary here.",
            },
            "file": "model.pth",
            "endpoint": None,
            "status": "unsafe",
            "issues": [
                {"type": "vulnerability", "description": "Test issue", "severity": "high", "attack_type": "evasion"}
            ],
        }
        formatted_output = format_text_output(result)
        self.assertIn("=== Adversarial Robustness Test Report ===", formatted_output)
        self.assertIn("Module: AdversarialTesting", formatted_output)
        self.assertIn("Framework: pytorch", formatted_output)
        self.assertIn("Status: UNSAFE", formatted_output)
        self.assertIn("Test issue", formatted_output)

    def test_write_output_json(self):
        """Test writing output in JSON format."""
        result = {"key": "value"}
        with patch("builtins.print") as mock_print:
            write_output(result, "json")
            mock_print.assert_called_once_with('{\n    "key": "value"\n}')

    def test_write_output_text(self):
        """Test writing output in text format."""
        result = {
            "module": "AdversarialTesting",
            "metadata": {
                "framework": "pytorch",
                "test_samples": 10,
                "scan_time": "1m",
                "summary": "Test summary here.",
            },
            "file": "model.pth",
            "endpoint": None,
            "status": "unsafe",
            "issues": [],
        }
        with patch("builtins.print") as mock_print:
            write_output(result, "text")
            mock_print.assert_called()

if __name__ == "__main__":
    unittest.main()
