#!/usr/bin/env python3
"""
Local test runner for LLM text refinement
Runs the test cases without needing the full API
"""

import asyncio
import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, '/config/workspace/gitea/DoR-Dash/backend')

from app.api.endpoints.text_testing import TEST_CASES, run_single_test
from app.api.endpoints.text import TextRefinementRequest

# Mock user class
class MockUser:
    def __init__(self):
        self.id = 1
        self.role = "admin"
        self.username = "test_user"

async def run_tests():
    """Run all test cases locally"""
    print("🧪 Running LLM Text Refinement Test Suite")
    print("=" * 50)
    
    mock_user = MockUser()
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📝 Test {i}/{len(TEST_CASES)}: {test_case.name}")
        print(f"Input: '{test_case.input_text[:60]}{'...' if len(test_case.input_text) > 60 else ''}'")
        
        try:
            result = await run_single_test(test_case, mock_user)
            results.append(result)
            
            # Show results
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"Status: {status}")
            print(f"Length ratio: {result.length_ratio:.2f}x")
            
            if result.output_text != "ERROR":
                print(f"Output: '{result.output_text[:60]}{'...' if len(result.output_text) > 60 else ''}'")
            
            if result.issues:
                print(f"Issues: {', '.join(result.issues)}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test_name": test_case.name,
                "passed": False,
                "issues": [str(e)],
                "length_ratio": 0
            })
        
        # Small delay
        await asyncio.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    avg_ratio = sum(r.length_ratio for r in results if hasattr(r, 'length_ratio') and r.length_ratio > 0) / max(1, len([r for r in results if hasattr(r, 'length_ratio') and r.length_ratio > 0]))
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {(passed/total*100):.1f}%")
    print(f"Average length ratio: {avg_ratio:.2f}x")
    
    if failed > 0:
        print(f"\n❌ {failed} tests failed. Check output above for details.")
    else:
        print(f"\n✅ All tests passed! LLM is behaving conservatively.")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")