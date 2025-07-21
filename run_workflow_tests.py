"""
Run workflow tests based on WORKFLOW_EXAMPLES.md
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all workflow tests"""
    print("=" * 60)
    print("Running Workflow Tests")
    print("=" * 60)
    print()
    
    # Test categories
    test_suites = [
        {
            'name': 'Healthcare Workflows E2E',
            'path': 'tests/e2e/test_healthcare_workflows.py',
            'markers': '-m e2e'
        },
        {
            'name': 'Office Workflows E2E', 
            'path': 'tests/e2e/test_office_workflows.py',
            'markers': '-m e2e'
        },
        {
            'name': 'Workflow Integration',
            'path': 'tests/integration/test_workflow_integration.py',
            'markers': '-m integration'
        }
    ]
    
    results = []
    
    for suite in test_suites:
        print(f"\n[Running {suite['name']}]")
        print("-" * 40)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            suite['path'],
            '-v',  # Verbose
            '--tb=short',  # Short traceback
            suite['markers']
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Store result
        results.append({
            'suite': suite['name'],
            'success': result.returncode == 0,
            'return_code': result.returncode
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_passed = sum(1 for r in results if r['success'])
    total_failed = len(results) - total_passed
    
    for result in results:
        status = "PASSED" if result['success'] else "FAILED"
        print(f"{result['suite']}: {status}")
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    
    # Return overall success
    return total_failed == 0

if __name__ == "__main__":
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)