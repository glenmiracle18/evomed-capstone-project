"""
Integration Tests for African Population-Aware BRCA1 Variant Analysis API

This test suite validates the complete API workflow including:
- API endpoint functionality
- Evo2 model integration
- Population service integration
- Response format validation
"""

import asyncio
import json
import time
import requests
from typing import Dict, List, Any
import unittest
from unittest.mock import patch, Mock


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for the variant analysis API"""
    
    def setUp(self):
        """Set up test environment"""
        # API endpoint (adjust based on deployment)
        self.api_base_url = "https://your-endpoint.modal.run"  # Update with actual endpoint
        
        # Test variant data
        self.test_variants = [
            {
                "name": "HbS Sickle Cell Variant",
                "data": {
                    "variant_position": 5227002,
                    "alternative": "A",
                    "genome": "hg38",
                    "chromosome": "chr11",
                    "use_african_adjustment": True
                },
                "expected_type": "likely_benign"
            },
            {
                "name": "BRCA1 Pathogenic Variant",
                "data": {
                    "variant_position": 43057063,
                    "alternative": "G",
                    "genome": "hg38", 
                    "chromosome": "chr17",
                    "use_african_adjustment": True
                },
                "expected_type": "likely_pathogenic"
            },
            {
                "name": "Common African Variant",
                "data": {
                    "variant_position": 158481978,
                    "alternative": "C",
                    "genome": "hg38",
                    "chromosome": "chr2",
                    "use_african_adjustment": True
                },
                "expected_type": "likely_benign"
            }
        ]
        
        self.integration_results = []
    
    def test_api_endpoint_availability(self):
        """Test API endpoint is available and responding"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            print("✓ API endpoint is available")
        except requests.RequestException as e:
            self.skipTest(f"API endpoint not available: {e}")
    
    def test_variant_analysis_with_african_adjustment(self):
        """Test variant analysis with African population adjustment enabled"""
        for variant in self.test_variants:
            with self.subTest(variant=variant["name"]):
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{self.api_base_url}/analyze_variant",
                        json=variant["data"],
                        timeout=30
                    )
                    
                    response_time = time.time() - start_time
                    
                    # Validate response
                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    
                    # Validate response structure
                    self.assertIn("delta_score", result)
                    self.assertIn("adjusted_score", result)
                    self.assertIn("classification", result)
                    self.assertIn("population_frequency", result)
                    self.assertIn("adjustment_applied", result)
                    
                    # Validate performance requirement (<5 seconds)
                    self.assertLess(response_time, 5.0, 
                                  f"Response time {response_time:.2f}s exceeds 5s requirement")
                    
                    # Store results for analysis
                    self.integration_results.append({
                        "variant": variant["name"],
                        "response_time": response_time,
                        "delta_score": result["delta_score"],
                        "adjusted_score": result["adjusted_score"],
                        "classification": result["classification"],
                        "adjustment": result.get("adjustment_applied", 0),
                        "expected": variant["expected_type"],
                        "matches_expected": result["classification"] == variant["expected_type"]
                    })
                    
                    print(f"✓ {variant['name']}: {result['classification']} "
                          f"(score: {result['adjusted_score']:.3f}, "
                          f"time: {response_time:.2f}s)")
                    
                except requests.RequestException as e:
                    self.fail(f"API request failed for {variant['name']}: {e}")
    
    def test_variant_analysis_without_african_adjustment(self):
        """Test variant analysis with African adjustment disabled for comparison"""
        test_variant = self.test_variants[0]  # HbS variant
        variant_data = test_variant["data"].copy()
        variant_data["use_african_adjustment"] = False
        
        try:
            response = requests.post(
                f"{self.api_base_url}/analyze_variant",
                json=variant_data,
                timeout=30
            )
            
            self.assertEqual(response.status_code, 200)
            result_without_adjustment = response.json()
            
            # Now test with adjustment
            variant_data["use_african_adjustment"] = True
            response = requests.post(
                f"{self.api_base_url}/analyze_variant",
                json=variant_data,
                timeout=30
            )
            
            result_with_adjustment = response.json()
            
            # Validate that adjustment affects the score
            self.assertNotEqual(
                result_without_adjustment["adjusted_score"],
                result_with_adjustment["adjusted_score"]
            )
            
            # African adjustment should reduce pathogenicity for this variant
            self.assertLess(
                result_with_adjustment["adjusted_score"],
                result_without_adjustment["adjusted_score"]
            )
            
            print(f"✓ African adjustment effect demonstrated:")
            print(f"  Without adjustment: {result_without_adjustment['adjusted_score']:.3f}")
            print(f"  With adjustment: {result_with_adjustment['adjusted_score']:.3f}")
            print(f"  Difference: {result_without_adjustment['adjusted_score'] - result_with_adjustment['adjusted_score']:.3f}")
            
        except requests.RequestException as e:
            self.fail(f"Comparison test failed: {e}")
    
    def test_api_error_handling(self):
        """Test API error handling for invalid inputs"""
        invalid_requests = [
            {
                "name": "Missing chromosome",
                "data": {
                    "variant_position": 5227002,
                    "alternative": "A",
                    "genome": "hg38",
                    "use_african_adjustment": True
                }
            },
            {
                "name": "Invalid genome",
                "data": {
                    "variant_position": 5227002,
                    "alternative": "A",
                    "genome": "invalid",
                    "chromosome": "chr11",
                    "use_african_adjustment": True
                }
            },
            {
                "name": "Invalid position",
                "data": {
                    "variant_position": -1,
                    "alternative": "A",
                    "genome": "hg38",
                    "chromosome": "chr11", 
                    "use_african_adjustment": True
                }
            }
        ]
        
        for invalid_request in invalid_requests:
            with self.subTest(test=invalid_request["name"]):
                try:
                    response = requests.post(
                        f"{self.api_base_url}/analyze_variant",
                        json=invalid_request["data"],
                        timeout=10
                    )
                    
                    # Should return error status
                    self.assertNotEqual(response.status_code, 200)
                    print(f"✓ {invalid_request['name']}: Correctly rejected (status {response.status_code})")
                    
                except requests.RequestException as e:
                    self.fail(f"Error handling test failed for {invalid_request['name']}: {e}")
    
    def test_concurrent_requests(self):
        """Test API performance under concurrent load"""
        import concurrent.futures
        import threading
        
        def make_request():
            variant_data = self.test_variants[0]["data"]
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/analyze_variant",
                    json=variant_data,
                    timeout=30
                )
                response_time = time.time() - start_time
                
                return {
                    "success": response.status_code == 200,
                    "response_time": response_time,
                    "thread_id": threading.current_thread().ident
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": time.time() - start_time
                }
        
        # Test with 5 concurrent requests
        concurrent_requests = 5
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results) * 100
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        self.assertGreaterEqual(success_rate, 80.0, "Success rate should be at least 80% under concurrent load")
        self.assertLess(avg_response_time, 10.0, "Average response time should be under 10s under load")
        
        print(f"✓ Concurrent load test:")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Average response time: {avg_response_time:.2f}s")
        print(f"  Failed requests: {len(failed_requests)}")
    
    def tearDown(self):
        """Print integration test summary"""
        if hasattr(self, 'integration_results') and self.integration_results:
            print(f"\n{'='*60}")
            print("INTEGRATION TEST RESULTS SUMMARY")
            print(f"{'='*60}")
            
            for result in self.integration_results:
                status = "✓" if result["matches_expected"] else "✗"
                print(f"{status} {result['variant']}: {result['classification']} "
                      f"(expected: {result['expected']})")
                print(f"  Score: {result['adjusted_score']:.3f} "
                      f"(Δ: {result['delta_score']:.3f}, adj: {result['adjustment']:.3f})")
                print(f"  Response time: {result['response_time']:.2f}s")
                print()


class TestPopulationServiceIntegration(unittest.TestCase):
    """Integration tests for population service with gnomAD API"""
    
    def setUp(self):
        from population_service import PopulationFrequencyService
        self.service = PopulationFrequencyService()
    
    def test_gnomad_integration(self):
        """Test integration with gnomAD API for real variant data"""
        test_variants = [
            ("chr11", 5227002, "A"),  # HbS variant
            ("chr17", 43057063, "G"), # BRCA1 variant
        ]
        
        for chrom, pos, alt in test_variants:
            with self.subTest(variant=f"{chrom}:{pos}:{alt}"):
                try:
                    freq_data = self.service.get_population_frequency(chrom, pos, alt)
                    
                    if freq_data:
                        self.assertIn('afr', freq_data)
                        self.assertIn('total', freq_data)
                        
                        # Validate frequency values are reasonable (0-1)
                        if freq_data['afr'] is not None:
                            self.assertGreaterEqual(freq_data['afr'], 0.0)
                            self.assertLessEqual(freq_data['afr'], 1.0)
                        
                        if freq_data['total'] is not None:
                            self.assertGreaterEqual(freq_data['total'], 0.0)
                            self.assertLessEqual(freq_data['total'], 1.0)
                        
                        print(f"✓ {chrom}:{pos}:{alt} - AFR: {freq_data['afr']}, Global: {freq_data['total']}")
                    else:
                        print(f"⚠ {chrom}:{pos}:{alt} - No frequency data available")
                        
                except Exception as e:
                    self.fail(f"Population service integration failed for {chrom}:{pos}:{alt}: {e}")


if __name__ == '__main__':
    print("Starting Integration Tests for African Population-Aware Variant Analysis")
    print("="*80)
    
    # Run tests
    test_loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(test_loader.loadTestsFromTestCase(TestAPIIntegration))
    suite.addTests(test_loader.loadTestsFromTestCase(TestPopulationServiceIntegration))
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print final summary
    print(f"\n{'='*80}")
    print("INTEGRATION TEST FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n🎉 All integration tests passed! System is ready for deployment.")
    else:
        print(f"\n⚠️  Integration issues detected. Review failures above.")
        
        if result.failures:
            print("\nFailures:")
            for test, error in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, error in result.errors:
                print(f"- {test}")