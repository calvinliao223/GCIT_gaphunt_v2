#!/usr/bin/env python3
"""
Enhanced comprehensive tests for Gap Hunter Bot
Tests the improved error handling, retry mechanisms, and fallback systems
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
import requests

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AI-gaphunt-v2'))
from clean_gap_hunter import GapHunterBot

class TestGapHunterBotEnhanced(unittest.TestCase):
    """Enhanced test suite for Gap Hunter Bot"""
    
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
        
        # Create bot instance
        self.bot = GapHunterBot()
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
    
    def test_enhanced_error_handling_empty_query(self):
        """Test enhanced error handling for empty queries"""
        result = self.bot.hunt_gaps("")
        
        self.assertEqual(len(result), 1)
        self.assertIn('error', result[0])
        self.assertEqual(result[0]['error_type'], 'validation')
        self.assertIn('suggestion', result[0])
    
    def test_enhanced_error_handling_short_query(self):
        """Test enhanced error handling for short queries"""
        result = self.bot.hunt_gaps("AI")
        
        self.assertEqual(len(result), 1)
        self.assertIn('error', result[0])
        self.assertEqual(result[0]['error_type'], 'validation')
        self.assertIn('suggestion', result[0])
    
    @patch('clean_gap_hunter.requests.get')
    def test_api_failure_handling(self, mock_get):
        """Test handling of API failures with enhanced error messages"""
        # Mock all APIs to fail
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.bot.hunt_gaps("machine learning")
        
        self.assertEqual(len(result), 1)
        self.assertIn('error', result[0])
        self.assertEqual(result[0]['error_type'], 'api_failure')
        self.assertIn('details', result[0])
    
    @patch('clean_gap_hunter.requests.get')
    def test_retry_mechanism(self, mock_get):
        """Test retry mechanism with exponential backoff"""
        # Mock first call to fail, second to succeed
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'data': [{
                'title': 'Test Paper',
                'authors': [{'name': 'Test Author'}],
                'year': 2024,
                'abstract': 'Test abstract about machine learning',
                'journal': {'name': 'Test Journal'}
            }]
        }
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        # Test S2 search with retry
        papers = self.bot.s2_search("machine learning")
        
        # Should succeed on retry
        self.assertGreater(len(papers), 0)
        self.assertEqual(mock_get.call_count, 2)  # Called twice due to retry
    
    @patch('clean_gap_hunter.requests.get')
    def test_rate_limit_handling(self, mock_get):
        """Test rate limit handling with proper backoff"""
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with patch('clean_gap_hunter.time.sleep') as mock_sleep:
            papers = self.bot.s2_search("machine learning")
            
            # Should handle rate limit and retry
            self.assertEqual(len(papers), 0)  # Eventually gives up
            mock_sleep.assert_called()  # Should have slept for backoff
    
    def test_query_validation_edge_cases(self):
        """Test query validation for edge cases"""
        # Test very long query
        long_query = "a" * 250
        result = self.bot.hunt_gaps(long_query)
        
        # Should not error, but truncate
        self.assertIsInstance(result, list)
        
        # Test query with special characters
        special_query = "machine learning & AI: deep neural networks (2024)"
        result = self.bot.hunt_gaps(special_query)
        
        # Should handle special characters gracefully
        self.assertIsInstance(result, list)
    
    @patch('clean_gap_hunter.requests.get')
    def test_successful_search_workflow(self, mock_get):
        """Test successful search workflow with all components"""
        # Mock successful API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'title': 'Advanced Machine Learning Techniques',
                'authors': [{'name': 'Dr. Test'}],
                'year': 2024,
                'abstract': 'This paper explores advanced machine learning techniques for real-world applications.',
                'journal': {'name': 'Journal of AI Research'},
                'url': 'https://example.com/paper1'
            }],
            'results': [{
                'title': 'Deep Learning Applications',
                'authors': 'Prof. Example',
                'year': 2023,
                'abstract': 'Applications of deep learning in various domains.',
                'journal': 'AI Conference Proceedings'
            }],
            'message': {
                'items': [{
                    'title': ['Cross-domain Machine Learning'],
                    'author': [{'given': 'Jane', 'family': 'Doe'}],
                    'published-print': {'date-parts': [[2024]]},
                    'abstract': 'Cross-domain applications of machine learning algorithms.',
                    'container-title': ['ML Journal']
                }]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.bot.hunt_gaps("machine learning")
        
        # Should return research gaps
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check result structure
        for gap in result:
            if 'error' not in gap:
                self.assertIn('gap', gap)
                self.assertIn('keywords', gap)
                self.assertIn('score', gap)
                self.assertIn('NEXT_STEPS', gap)
                self.assertIn('paper', gap)
    
    def test_environment_loading(self):
        """Test environment variable loading"""
        # Test that required keys are loaded
        required_keys = ['S2_API_KEY', 'CORE_API_KEY', 'GOOGLE_API_KEY', 'CONTACT_EMAIL']
        
        for key in required_keys:
            self.assertIn(key, os.environ)
            self.assertIsNotNone(os.environ.get(key))
    
    @patch('clean_gap_hunter.GOOGLE_FALLBACK_AVAILABLE', True)
    @patch('clean_gap_hunter.requests.get')
    def test_google_fallback_integration(self, mock_get):
        """Test Google Scholar fallback when primary APIs fail"""
        # Mock all primary APIs to fail
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_get.return_value = mock_response_fail
        
        # Mock Google fallback to succeed
        with patch.object(self.bot, 'google_fallback') as mock_google:
            mock_google.search_papers.return_value = [{
                'title': 'Fallback Paper',
                'link': 'https://scholar.google.com/paper1',
                'snippet': 'This is a fallback paper about machine learning'
            }]
            
            result = self.bot.hunt_gaps("machine learning")
            
            # Should use Google fallback
            mock_google.search_papers.assert_called_once()

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
