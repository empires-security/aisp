import unittest
from unittest.mock import patch, MagicMock
import logging
import json
import argparse
from io import StringIO
from datetime import datetime
from pathlib import Path

from main import setup_logging, parse_args, format_text_output

class TestMain(unittest.TestCase):
    def test_setup_logging(self):
        logger = setup_logging()

        # Verify logger type
        self.assertIsInstance(logger, logging.Logger)

        # Check the logger's effective level
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

        # Test if logging produces output at INFO level
        with self.assertLogs(logger, level='INFO') as log_capture:
            logger.info("Test log message")
        self.assertIn("Test log message", log_capture.output[0])

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args_with_file(self, mock_parse_args):
        # Simulate arguments with --file
        mock_parse_args.return_value = argparse.Namespace(
            file='model.pth',
            endpoint=None,
            framework='openai',
            model_name='gpt-4',
            probe_suites=['injection'],
            detector_suites=None,
            buff_suites=None,
            api_key='test-api-key',
            request_format=None,
            response_key=None,
            headers=None,
            output='json',
            output_file=None
        )
        args = parse_args()
        self.assertEqual(args.file, 'model.pth')
        self.assertIsNone(args.endpoint)
        self.assertEqual(args.framework, 'openai')
        self.assertEqual(args.model_name, 'gpt-4')
        self.assertEqual(args.output, 'json')

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args_with_endpoint(self, mock_parse_args):
        # Simulate arguments with --endpoint
        mock_parse_args.return_value = argparse.Namespace(
            file=None,
            endpoint='https://api.example.com',
            framework='huggingface',
            model_name='bert-base',
            probe_suites=['xss'],
            detector_suites=['detector1'],
            buff_suites=['buff1'],
            api_key=None,
            request_format='json',
            response_key='response',
            headers='{"Authorization": "Bearer xyz"}',
            output='text',
            output_file='results.txt'
        )
        args = parse_args()
        self.assertEqual(args.endpoint, 'https://api.example.com')
        self.assertEqual(args.framework, 'huggingface')
        self.assertEqual(args.model_name, 'bert-base')
        self.assertEqual(args.output, 'text')
        self.assertEqual(args.output_file, 'results.txt')
        self.assertEqual(args.headers, '{"Authorization": "Bearer xyz"}')

    def test_format_text_output(self):
        # Mock the input data for formatting
        mock_data = {
            'module': 'LLM Security Testing',
            'metadata': {
                'framework': 'openai',
                'model_name': 'gpt-4',
                'garak_version': '1.0.0',
                'summary': 'Test Summary',
                'test_details': {
                    'probe_suites': ['injection'],
                    'detector_suites': None,
                    'buff_suites': None,
                    'total_probes': 10,
                    'completed_tests': 8,
                    'failed_tests': 2,
                    'error_details': [],
                    'completed_probes': ['probe1', 'probe2'],
                    'failed_probes': ['probe3'],
                    'skipped_probes': []
                }
            },
            'file': None,
            'endpoint': 'https://api.example.com',
            'status': 'completed',
            'issues': [
                {
                    'type': 'injection',
                    'description': 'SQL Injection found',
                    'severity': 'high',
                    'attack_type': 'injection',
                    'attack_details': 'Details about the attack'
                }
            ]
        }
        output = format_text_output(mock_data)
        self.assertIn('LLM Security Test Report', output)
        self.assertIn('Framework: openai', output)
        self.assertIn('Model: gpt-4', output)
        self.assertIn('Vulnerabilities Found:', output)
        self.assertIn('SQL Injection found', output)
        self.assertIn('Severity: high', output)
        self.assertIn('Details about the attack', output)

if __name__ == '__main__':
    unittest.main()
