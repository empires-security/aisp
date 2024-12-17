import unittest
from unittest.mock import patch, MagicMock
from scanner import LLMSecurityScanner
from garak import _config

class TestLLMSecurityScanner(unittest.TestCase):
    def setUp(self):
        self.default_scanner = LLMSecurityScanner(
            model_path="dummy_model_path",
            endpoint="http://dummy-endpoint.com",
            model_name="dummy_model",
            api_key="test_api_key"
        )

    def test_initialization_defaults(self):
        """Test initialization with default probe suites."""
        self.assertEqual(self.default_scanner.probe_suites, ["injection", "xss", "prompt_leak"])
        self.assertEqual(self.default_scanner.detector_suites, [])
        self.assertEqual(self.default_scanner.buff_suites, [])
        self.assertEqual(self.default_scanner.headers, {})
        self.assertIsNone(self.default_scanner.request_format)

    @patch("garak._config.load_base_config")
    def test_configure_garak(self, mock_load_base_config):
        """Test Garak configuration setup."""
        self.default_scanner._configure_garak()

        # Validate Garak configurations
        self.assertEqual(_config.system.verbose, 1)
        self.assertEqual(_config.system.parallel_requests, 1)
        self.assertEqual(_config.plugins.model_type, "rest")

        mock_load_base_config.assert_called_once()

    def test_parse_specs_with_invalid_spec(self):
        """Test parsing plugin specifications with invalid spec."""
        invalid_scanner = LLMSecurityScanner(detector_suites=["invalid_suite"])
        resolved = invalid_scanner._parse_specs("detector")
        
        self.assertEqual(resolved, [])
    
    def test_prepare_results(self):
        """Test result preparation logic."""
        test_details = {
            "completed_tests": 1,
            "failed_tests": 0,
            "completed_probes": ["probe1"],
            "failed_probes": [],
            "skipped_probes": [],
            "error_details": []  # Include this to match method requirements
        }
        issues = [{"type": "error", "description": "Issue Found"}]
        results = self.default_scanner._prepare_results(issues, test_details)

        self.assertEqual(results["status"], "unsafe")
        self.assertIn("Issue Found", results["issues"][0]["description"])

if __name__ == "__main__":
    unittest.main()
