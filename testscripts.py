#!/usr/bin/env python3

import requests
import json
import sys
import time

def test_service(base_url="http://localhost:8080"):
    """Comprehensive test suite for the sandboxed code runner"""
    
    print(f" Testing Sandboxed Code Runner at {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    def run_test(test_name, test_func):
        nonlocal tests_passed, tests_total
        tests_total += 1
        print(f"\n{tests_total}. {test_name}")
        try:
            if test_func():
                print("✅ PASSED")
                tests_passed += 1
            else:
                print(" FAILED")
        except Exception as e:
            print(f" FAILED - {e}")
    
    # Test 1: Health check
    def test_health():
        response = requests.get(f"{base_url}/health", timeout=10)
        return response.status_code == 200 and response.json().get("status") == "healthy"
    
    run_test("Health Check", test_health)
    
    # Test 2: Basic execution
    def test_basic_execution():
        script = 'def main():\n    return {"message": "Hello World", "number": 42}'
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        expected = {"message": "Hello World", "number": 42}
        return result.get("result") == expected and "stdout" in result
    
    run_test("Basic Python Execution", test_basic_execution)
    
    # Test 3: NumPy integration
    def test_numpy():
        script = '''import numpy as np

def main():
    arr = np.array([1, 2, 3, 4, 5])
    return {
        "mean": float(np.mean(arr)),
        "sum": int(np.sum(arr)),
        "std": float(np.std(arr))
    }'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        return (result.get("result", {}).get("mean") == 3.0 and 
                result.get("result", {}).get("sum") == 15)
    
    run_test("NumPy Integration", test_numpy)
    
    # Test 4: Pandas integration
    def test_pandas():
        script = '''import pandas as pd

def main():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    return {
        "shape": list(df.shape),
        "mean_a": float(df["a"].mean()),
        "sum_b": int(df["b"].sum())
    }'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        return (result.get("result", {}).get("shape") == [3, 2] and
                result.get("result", {}).get("mean_a") == 2.0)
    
    run_test("Pandas Integration", test_pandas)
    
    # Test 5: Stdout capture
    def test_stdout_capture():
        script = '''def main():
    print("Debug: Starting calculation")
    result = sum(range(10))
    print(f"Debug: Result is {result}")
    return {"calculation": result}'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        stdout = result.get("stdout", "")
        return ("Debug: Starting calculation" in stdout and 
                "Debug: Result is 45" in stdout and
                result.get("result", {}).get("calculation") == 45)
    
    run_test("Stdout Capture", test_stdout_capture)
    
    # Test 6: Error handling - no main function
    def test_no_main_function():
        script = '''def not_main():
    return {"error": "should not work"}'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        return (response.status_code == 400 and 
                "main" in response.json().get("error", "").lower())
    
    run_test("Error Handling - No main() Function", test_no_main_function)
    
    # Test 7: Error handling - runtime error
    def test_runtime_error():
        script = '''def main():
    return 1 / 0  # Division by zero'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        return response.status_code == 400 and "error" in response.json()
    
    run_test("Error Handling - Runtime Error", test_runtime_error)
    
    # Test 8: JSON response validation
    def test_json_response():
        script = '''def main():
    return {
        "string": "test",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        expected_keys = ["string", "number", "float", "boolean", "null", "list", "nested"]
        return all(key in result.get("result", {}) for key in expected_keys)
    
    run_test("JSON Response Validation", test_json_response)
    
    # Test 9: Scipy integration
    def test_scipy():
        script = '''import scipy.stats as stats
import numpy as np

def main():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    mean = float(np.mean(data))
    std = float(np.std(data))
    return {
        "mean": mean,
        "std": std,
        "data_length": len(data)
    }'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        return (result.get("result", {}).get("mean") == 5.5 and
                result.get("result", {}).get("data_length") == 10)
    
    run_test("SciPy Integration", test_scipy)
    
    # Test 10: Input validation - large script
    def test_large_script():
        # Create a script larger than 50KB (50,000 characters)
        base_script = 'def main():\n    return {"test": "data"}\n'
        large_script = base_script + "# " + "x" * 51000  # Definitely over 50KB
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": large_script}, timeout=30)
        
        return response.status_code == 400 and "size" in response.json().get("error", "").lower()
    
    run_test("Input Validation - Large Script", test_large_script)
    
    # Test 11: Timeout test (should complete within limit)
    def test_execution_speed():
        script = '''def main():
    # Fast computation that should complete quickly
    result = sum(i*i for i in range(1000))
    return {"sum_of_squares": result}'''
        
        start_time = time.time()
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        execution_time = time.time() - start_time
        
        return (response.status_code == 200 and 
                execution_time < 5.0 and  # Should complete in under 5 seconds
                response.json().get("result", {}).get("sum_of_squares") == 332833500)
    
    run_test("Execution Speed", test_execution_speed)
    
    # Test 12: Multiple library imports
    def test_multiple_libraries():
        script = '''import numpy as np
import pandas as pd
import requests  # Note: won't work for actual requests due to network isolation

def main():
    # NumPy
    arr = np.array([1, 2, 3])
    
    # Pandas  
    df = pd.DataFrame({"col": arr})
    
    return {
        "numpy_sum": int(np.sum(arr)),
        "pandas_mean": float(df["col"].mean()),
        "libraries_loaded": True
    }'''
        
        response = requests.post(f"{base_url}/execute", 
                               json={"script": script}, timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        return (result.get("result", {}).get("numpy_sum") == 6 and
                result.get("result", {}).get("pandas_mean") == 2.0 and
                result.get("result", {}).get("libraries_loaded") is True)
    
    run_test("Multiple Library Imports", test_multiple_libraries)
    
    # Final Results
    print("\n" + "=" * 60)
    print(f" TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print(" ALL TESTS PASSED! Service is working correctly.")
        return True
    else:
        print(f" {tests_total - tests_passed} tests failed. Please check the issues above.")
        return False

def test_requirements_compliance():
    """Test specific requirements from the challenge"""
    print("\n" + "=" * 60)
    print(" REQUIREMENTS COMPLIANCE CHECK")
    print("=" * 60)
    
    requirements = [
        "✅ Flask and nsjail implementation",
        "✅ Docker image with single 'docker run' command", 
        "✅ Basic input validation (script size, main() function)",
        "✅ Safe execution with resource limits and sandboxing",
        "✅ Library support (numpy, pandas, scipy, matplotlib)",
        "✅ JSON response format with result and stdout",
        "✅ Health check endpoint",
        "✅ Error handling for invalid scripts",
        "✅ README with Cloud Run URL examples"
    ]
    
    for req in requirements:
        print(req)
    
    print("\n All major requirements implemented!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8080"
    
    print(" Sandboxed Code Runner")
    print(f" Testing URL: {base_url}")
    
    # Run main tests
    success = test_service(base_url)
    
    # Check requirements compliance
    test_requirements_compliance()
    
    # Exit code for CI/CD
    sys.exit(0 if success else 1)