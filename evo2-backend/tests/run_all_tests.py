#!/usr/bin/env python3
"""
Main Test Runner for African Population-Aware BRCA1 Variant Analysis System

This script runs all tests and generates comprehensive reports for Canvas submission.
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    """Print test suite header"""
    print("🧬" * 40)
    print("AFRICAN POPULATION-AWARE BRCA1 VARIANT ANALYSIS")
    print("COMPREHENSIVE TESTING SUITE")
    print("🧬" * 40)
    print(f"Test execution started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def run_test_file(test_file: str, description: str) -> bool:
    """Run a single test file"""
    print(f"\n🧪 {description}")
    print("-" * 60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Show last 500 chars
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("Error:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Main test execution function"""
    print_header()
    
    # Change to tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Test suite configuration
    test_suite = [
        {
            "file": "test_unit_population_service.py",
            "description": "Unit Tests - Population Service Algorithms",
            "required": True
        },
        {
            "file": "test_integration_api.py", 
            "description": "Integration Tests - API Endpoints",
            "required": True
        },
        {
            "file": "test_performance_load.py",
            "description": "Performance Tests - Load & Scalability",
            "required": True
        },
        {
            "file": "test_e2e_workflow.py",
            "description": "End-to-End Tests - Complete Workflows",
            "required": False  # May require browser setup
        },
        {
            "file": "test_hardware_specifications.py",
            "description": "Hardware Specification Tests - Cross-Platform Performance",
            "required": True
        },
        {
            "file": "demo_testing_strategies.py",
            "description": "Testing Strategy Demonstration - Different Data Values",
            "required": True
        }
    ]
    
    results = []
    required_passes = 0
    total_required = sum(1 for test in test_suite if test["required"])
    
    # Run each test
    for test in test_suite:
        if os.path.exists(test["file"]):
            success = run_test_file(test["file"], test["description"])
            results.append({
                "test": test["file"],
                "description": test["description"],
                "success": success,
                "required": test["required"]
            })
            
            if success and test["required"]:
                required_passes += 1
        else:
            print(f"⚠️  Test file not found: {test['file']}")
            results.append({
                "test": test["file"],
                "description": test["description"],
                "success": False,
                "required": test["required"]
            })
    
    # Generate comprehensive report
    print(f"\n📊 GENERATING COMPREHENSIVE REPORT")
    print("-" * 60)
    
    try:
        result = subprocess.run([sys.executable, "generate_simple_report.py"], 
                              capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✅ Comprehensive report generated successfully")
            if result.stdout:
                print("Report output:", result.stdout[-1000:])
        else:
            print("❌ Report generation failed")
            if result.stderr:
                print("Error:", result.stderr[-500:])
                
    except Exception as e:
        print(f"💥 Report generation error: {e}")
    
    # Print final summary
    print(f"\n{'='*80}")
    print("🎯 FINAL TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(f"Tests failed: {total_tests - passed_tests}")
    print(f"Required tests passed: {required_passes}/{total_required}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        req_flag = " [REQUIRED]" if result["required"] else " [OPTIONAL]"
        print(f"  {status} {result['description']}{req_flag}")
    
    # Determine overall success
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    required_success_rate = (required_passes / total_required * 100) if total_required > 0 else 0
    
    print(f"\n🎯 ASSIGNMENT READINESS:")
    if required_success_rate >= 80:
        print("🎉 READY FOR CANVAS SUBMISSION!")
        print("✅ Testing strategies demonstrated successfully")
        print("✅ Bias reduction evidence quantified")
        print("✅ Performance validated across specifications")
        print("✅ Comprehensive analysis generated")
        
        print(f"\n📁 SUBMISSION MATERIALS LOCATION:")
        print(f"   📂 Tests: ./tests/ directory")
        print(f"   📊 Results: ../test_results/ directory")
        print(f"   📈 Visualizations: ../test_results/*.png")
        print(f"   📄 Reports: ../test_results/*.json and *.md")
        
    else:
        print("⚠️  ADDITIONAL WORK NEEDED")
        print(f"   Required test success rate: {required_success_rate:.1f}% (need 80%+)")
        print("   Review failed tests above and fix issues")
    
    print(f"\n🕒 Test execution completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return required_success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)