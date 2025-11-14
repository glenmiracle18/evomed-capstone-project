"""
Unit Tests for African Population Frequency Service

This test suite validates the core functionality of the population service
including frequency calculation, adjustment algorithms, and error handling.
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import population_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from population_service import PopulationFrequencyService


class TestPopulationFrequencyService(unittest.TestCase):
    """Unit tests for PopulationFrequencyService class"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize service with test database
        self.service = PopulationFrequencyService()
        self.service.db_path = self.db_path
        self.service._init_cache_db()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_adjustment_calculation_high_frequency(self):
        """Test adjustment for high-frequency African variants (>5%)"""
        freq_data = {
            'afr': 0.08,  # 8% frequency in African populations
            'total': 0.02  # 2% globally
        }
        
        adjustment = self.service.calculate_population_adjustment(0.5, freq_data)
        
        # Should apply +0.004 for >5% frequency + 0.003 population-specific
        expected = 0.007
        self.assertAlmostEqual(adjustment, expected, places=3)
    
    def test_adjustment_calculation_moderate_frequency(self):
        """Test adjustment for moderate-frequency African variants (1-5%)"""
        freq_data = {
            'afr': 0.03,  # 3% frequency in African populations
            'total': 0.01  # 1% globally
        }
        
        adjustment = self.service.calculate_population_adjustment(0.5, freq_data)
        
        # Should apply +0.002 for 1-5% frequency + 0.003 population-specific
        expected = 0.005
        self.assertAlmostEqual(adjustment, expected, places=3)
    
    def test_adjustment_calculation_low_frequency(self):
        """Test adjustment for low-frequency African variants (0.5-1%)"""
        freq_data = {
            'afr': 0.007,  # 0.7% frequency in African populations
            'total': 0.003  # 0.3% globally
        }
        
        adjustment = self.service.calculate_population_adjustment(0.5, freq_data)
        
        # Should apply +0.001 for 0.5-1% frequency + 0.003 population-specific
        expected = 0.004
        self.assertAlmostEqual(adjustment, expected, places=3)
    
    def test_adjustment_calculation_rare_variant(self):
        """Test adjustment for rare variants (<0.5%)"""
        freq_data = {
            'afr': 0.002,  # 0.2% frequency in African populations
            'total': 0.001  # 0.1% globally
        }
        
        adjustment = self.service.calculate_population_adjustment(0.5, freq_data)
        
        # Should apply only +0.003 for population-specific (no frequency bonus)
        expected = 0.003
        self.assertAlmostEqual(adjustment, expected, places=3)
    
    def test_adjustment_calculation_no_african_data(self):
        """Test adjustment when no African frequency data available"""
        freq_data = {
            'afr': None,
            'total': 0.001
        }
        
        adjustment = self.service.calculate_population_adjustment(0.5, freq_data)
        
        # Should return 0 when no African data available
        self.assertEqual(adjustment, 0.0)
    
    def test_cache_functionality(self):
        """Test database caching of frequency data"""
        # Test data
        chromosome = "chr11"
        position = 5227002
        alt = "A"
        test_data = {
            'afr': 0.05,
            'total': 0.02,
            'cached_at': '2025-01-01 00:00:00'
        }
        
        # Store in cache
        self.service._store_in_cache(chromosome, position, alt, test_data)
        
        # Retrieve from cache
        cached_data = self.service._get_from_cache(chromosome, position, alt)
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['afr'], 0.05)
        self.assertEqual(cached_data['total'], 0.02)
    
    @patch('requests.post')
    def test_gnomad_api_success(self, mock_post):
        """Test successful gnomAD API call"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'variant': {
                    'genome': {
                        'ac': 100,
                        'an': 1000,
                        'populations': [
                            {'id': 'afr', 'ac': 50, 'an': 500}
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        
        # Test API call
        freq_data = self.service._fetch_from_gnomad("chr11", 5227002, "A")
        
        self.assertIsNotNone(freq_data)
        self.assertEqual(freq_data['afr'], 0.1)  # 50/500
        self.assertEqual(freq_data['total'], 0.1)  # 100/1000
    
    @patch('requests.post')
    def test_gnomad_api_failure(self, mock_post):
        """Test gnomAD API failure handling"""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test API call
        freq_data = self.service._fetch_from_gnomad("chr11", 5227002, "A")
        
        self.assertIsNone(freq_data)
    
    def test_population_specific_detection(self):
        """Test detection of population-specific variants"""
        # Population-specific variant (high in AFR, low globally)
        freq_data = {
            'afr': 0.08,  # 8% in African populations
            'total': 0.02  # 2% globally
        }
        
        is_specific = self.service._is_population_specific(freq_data)
        self.assertTrue(is_specific)
        
        # Non-population-specific variant
        freq_data = {
            'afr': 0.02,  # 2% in African populations
            'total': 0.02  # 2% globally
        }
        
        is_specific = self.service._is_population_specific(freq_data)
        self.assertFalse(is_specific)
    
    def test_known_pathogenic_variants(self):
        """Test handling of known pathogenic variants"""
        # Test BRCA1 pathogenic variant (should not be adjusted)
        pathogenic_variants = [
            ("chr17", 43057063, "G"),  # BRCA1 c.68_69delAG
            ("chr17", 43094823, "C"),  # BRCA1 c.4327C>T
        ]
        
        for chrom, pos, alt in pathogenic_variants:
            freq_data = {'afr': 0.001, 'total': 0.0005}
            adjustment = self.service.calculate_population_adjustment(0.8, freq_data)
            
            # Pathogenic variants should get minimal adjustment
            self.assertLessEqual(adjustment, 0.003)


class TestBiasReductionScenarios(unittest.TestCase):
    """Test scenarios demonstrating bias reduction"""
    
    def setUp(self):
        self.service = PopulationFrequencyService()
    
    def test_sickle_cell_variant(self):
        """Test HbS (sickle cell) variant - protective in African populations"""
        freq_data = {
            'afr': 0.12,  # 12% in West African populations
            'total': 0.03  # 3% globally
        }
        
        # Simulated Evo2 delta score (might predict pathogenic)
        original_score = 0.7
        adjustment = self.service.calculate_population_adjustment(original_score, freq_data)
        adjusted_score = original_score - adjustment
        
        # Should significantly reduce pathogenicity prediction
        self.assertGreater(adjustment, 0.006)  # Strong adjustment
        self.assertLess(adjusted_score, 0.5)   # Now likely benign
    
    def test_g6pd_deficiency_variant(self):
        """Test G6PD deficiency variant - common in malaria endemic regions"""
        freq_data = {
            'afr': 0.08,  # 8% in African populations
            'total': 0.02  # 2% globally
        }
        
        original_score = 0.6
        adjustment = self.service.calculate_population_adjustment(original_score, freq_data)
        adjusted_score = original_score - adjustment
        
        # Should apply population-aware adjustment
        self.assertGreater(adjustment, 0.005)
        self.assertLess(adjusted_score, original_score)
    
    def test_true_pathogenic_preservation(self):
        """Test that truly pathogenic variants maintain classification"""
        freq_data = {
            'afr': 0.0001,  # Very rare even in African populations
            'total': 0.00005
        }
        
        original_score = 0.9  # High pathogenicity
        adjustment = self.service.calculate_population_adjustment(original_score, freq_data)
        adjusted_score = original_score - adjustment
        
        # Should maintain pathogenic classification
        self.assertLessEqual(adjustment, 0.003)  # Minimal adjustment
        self.assertGreater(adjusted_score, 0.7)  # Still pathogenic


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    
    # Load test cases
    suite = unittest.TestSuite()
    suite.addTests(test_loader.loadTestsFromTestCase(TestPopulationFrequencyService))
    suite.addTests(test_loader.loadTestsFromTestCase(TestBiasReductionScenarios))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"UNIT TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")