#!/usr/bin/env python3
"""
Comprehensive test suite for Gap Hunter Bot
Tests core functionality, error handling, and edge cases
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import requests

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI-gaphunt-v2'))

class TestGapHunterBot(unittest.TestCase):
    """Test cases for Gap Hunter Bot core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'S2_API_KEY': 'test_s2_key',
            'CORE_API_KEY': 'test_core_key',
            'GOOGLE_API_KEY': 'test_google_key',
            'CONTACT_EMAIL': 'test@example.com'
        })
        self.env_patcher.start()
        
        # Import after setting environment
        try:
            from clean_gap_hunter import GapHunterBot
            self.bot = GapHunterBot()
        except ImportError:
            self.skipTest("GapHunterBot not available")
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test bot initialization"""
        self.assertIsNotNone(self.bot)
        self.assertFalse(self.bot.greeting_shown)
    
    @patch('requests.get')
    def test_s2_search_success(self, mock_get):
        """Test successful S2 API search"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'title': 'Test Paper',
                    'authors': [{'name': 'Test Author'}],
                    'year': 2023,
                    'abstract': 'Test abstract'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = self.bot.s2_search("machine learning")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Paper')
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_s2_search_rate_limit(self, mock_get):
        """Test S2 API rate limit handling"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        results = self.bot.s2_search("machine learning")
        
        self.assertEqual(results, [])
    
    @patch('requests.get')
    def test_s2_search_timeout(self, mock_get):
        """Test S2 API timeout handling"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        results = self.bot.s2_search("machine learning")
        
        self.assertEqual(results, [])
    
    def test_s2_search_empty_query(self):
        """Test S2 search with empty query"""
        results = self.bot.s2_search("")
        self.assertEqual(results, [])
        
        results = self.bot.s2_search(None)
        self.assertEqual(results, [])
    
    def test_s2_search_missing_api_key(self):
        """Test S2 search without API key"""
        with patch.dict(os.environ, {'S2_API_KEY': ''}, clear=False):
            results = self.bot.s2_search("machine learning")
            self.assertEqual(results, [])
    
    @patch('requests.get')
    def test_core_search_success(self, mock_get):
        """Test successful CORE API search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Core Test Paper',
                    'authors': ['Core Author'],
                    'year': 2023
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = self.bot.core_search("machine learning")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Core Test Paper')
    
    @patch('requests.get')
    def test_crossref_search_success(self, mock_get):
        """Test successful Crossref API search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'items': [
                    {
                        'title': ['Crossref Test Paper'],
                        'author': [{'family': 'Crossref', 'given': 'Author'}],
                        'published': {'date-parts': [[2023]]}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        results = self.bot.crossref_search("machine learning")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], ['Crossref Test Paper'])
    
    def test_hunt_gaps_input_validation(self):
        """Test input validation in hunt_gaps method"""
        # Test empty query
        results = self.bot.hunt_gaps("")
        self.assertEqual(len(results), 1)
        self.assertIn('error', results[0])
        
        # Test None query
        results = self.bot.hunt_gaps(None)
        self.assertEqual(len(results), 1)
        self.assertIn('error', results[0])
        
        # Test very short query
        results = self.bot.hunt_gaps("ai")
        self.assertEqual(len(results), 1)
        self.assertIn('error', results[0])
    
    def test_extract_paper_info(self):
        """Test paper information extraction"""
        test_paper = {
            'title': 'Test Paper Title',
            'authors': [{'name': 'John Doe'}],
            'year': 2023,
            'journal': {'name': 'Test Journal'}
        }
        
        info = self.bot.extract_paper_info(test_paper)
        
        self.assertIn('title', info)
        self.assertIn('first_author', info)
        self.assertIn('year', info)
        self.assertIn('journal_name', info)
        
        self.assertEqual(info['title'], 'Test Paper Title')
        self.assertEqual(info['first_author'], 'Doe')
        self.assertEqual(info['year'], '2023')
    
    def test_extract_paper_info_missing_data(self):
        """Test paper extraction with missing data"""
        test_paper = {}
        
        info = self.bot.extract_paper_info(test_paper)
        
        self.assertEqual(info['title'], 'Data unavailable')
        self.assertEqual(info['first_author'], 'Data unavailable')
        self.assertEqual(info['year'], 'Data unavailable')
    
    def test_check_q1_journal(self):
        """Test Q1 journal checking"""
        # Test Q1 journal
        self.assertTrue(self.bot.check_q1_journal("Nature"))
        self.assertTrue(self.bot.check_q1_journal("IEEE Transactions on Pattern Analysis"))
        
        # Test non-Q1 journal
        self.assertFalse(self.bot.check_q1_journal("Random Journal"))
        self.assertFalse(self.bot.check_q1_journal(""))
        self.assertFalse(self.bot.check_q1_journal(None))
    
    def test_calculate_novelty_score(self):
        """Test novelty score calculation"""
        test_paper = {'year': 2023}
        
        # Test with gap indicating limitations
        score = self.bot.calculate_novelty_score(test_paper, "Limited understanding of machine learning")
        self.assertGreaterEqual(score, 3)
        self.assertLessEqual(score, 5)
        
        # Test with older paper
        old_paper = {'year': 2019}
        score = self.bot.calculate_novelty_score(old_paper, "Some research gap")
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 5)
    
    def test_generate_keywords(self):
        """Test keyword generation"""
        keywords = self.bot.generate_keywords("machine learning applications", "Limited scalability in healthcare")
        
        self.assertIsInstance(keywords, list)
        self.assertGreaterEqual(len(keywords), 3)
        self.assertLessEqual(len(keywords), 5)
    
    def test_generate_next_steps(self):
        """Test next steps generation"""
        keywords = ["machine", "learning", "healthcare"]
        next_steps = self.bot.generate_next_steps("Limited scalability", keywords)
        
        self.assertIsInstance(next_steps, str)
        self.assertLessEqual(len(next_steps), 200)  # Reasonable length check


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality"""
    
    def setUp(self):
        """Set up error handling tests"""
        try:
            from error_handler import (
                validate_input, handle_api_errors, safe_execute,
                is_valid_query, check_api_keys, create_error_response
            )
            self.validate_input = validate_input
            self.handle_api_errors = handle_api_errors
            self.safe_execute = safe_execute
            self.is_valid_query = is_valid_query
            self.check_api_keys = check_api_keys
            self.create_error_response = create_error_response
        except ImportError:
            self.skipTest("Error handler module not available")
    
    def test_is_valid_query(self):
        """Test query validation"""
        # Valid queries
        valid, msg = self.is_valid_query("machine learning")
        self.assertTrue(valid)
        self.assertEqual(msg, "")
        
        # Invalid queries
        valid, msg = self.is_valid_query("")
        self.assertFalse(valid)
        self.assertIn("empty", msg.lower())
        
        valid, msg = self.is_valid_query("ai")
        self.assertFalse(valid)
        self.assertIn("short", msg.lower())
        
        valid, msg = self.is_valid_query("a" * 300)
        self.assertFalse(valid)
        self.assertIn("long", msg.lower())
    
    def test_check_api_keys(self):
        """Test API key checking"""
        with patch.dict(os.environ, {'TEST_KEY': 'value'}, clear=True):
            missing = self.check_api_keys(['TEST_KEY', 'MISSING_KEY'])
            self.assertEqual(missing, ['MISSING_KEY'])
    
    def test_create_error_response(self):
        """Test error response creation"""
        response = self.create_error_response("Test error")
        
        self.assertIn('error', response)
        self.assertIn('type', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['error'], "Test error")
        self.assertEqual(response['type'], "error")
    
    def test_safe_execute(self):
        """Test safe execution wrapper"""
        # Test successful execution
        result = self.safe_execute(lambda: 42)
        self.assertEqual(result, 42)
        
        # Test failed execution with default
        result = self.safe_execute(lambda: 1/0, default_return="error")
        self.assertEqual(result, "error")


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading functionality"""
    
    def setUp(self):
        """Set up config loader tests"""
        try:
            from config_loader import validate_api_keys, get_api_key
            self.validate_api_keys = validate_api_keys
            self.get_api_key = get_api_key
        except ImportError:
            self.skipTest("Config loader module not available")
    
    def test_validate_api_keys(self):
        """Test API key validation"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_key',
            'S2_API_KEY': 'test_key',
            'CORE_API_KEY': 'test_key',
            'OPENAI_API_KEY': 'test_key'
        }, clear=True):
            status = self.validate_api_keys()
            
            self.assertIn('core_keys', status)
            self.assertIn('llm_keys', status)
            self.assertIn('all_core_available', status)
            self.assertIn('llm_providers_available', status)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestGapHunterBot))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestConfigLoader))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print(f"SUCCESS RATE: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
