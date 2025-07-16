#!/usr/bin/env python3
"""
Automated test runner with logging and report generation
"""

import sys
import os
from pathlib import Path
import subprocess
import json
import time
from datetime import datetime
import pandas as pd
import argparse
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class TestRunner:
    """Automated test runner with reporting"""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def run_test_suite(self, test_files: List[str]) -> Dict[str, Any]:
        """Run a suite of test files"""
        self.start_time = datetime.now()
        suite_results = {
            'start_time': self.start_time.isoformat(),
            'test_files': test_files,
            'results': [],
            'summary': {}
        }
        
        for test_file in test_files:
            print(f"\n{'='*60}")
            print(f"Running tests in: {test_file}")
            print(f"{'='*60}\n")
            
            result = self.run_single_test(test_file)
            suite_results['results'].append(result)
            
        self.end_time = datetime.now()
        suite_results['end_time'] = self.end_time.isoformat()
        suite_results['duration'] = (self.end_time - self.start_time).total_seconds()
        
        # Calculate summary
        suite_results['summary'] = self.calculate_summary(suite_results['results'])
        
        return suite_results
        
    def run_single_test(self, test_file: str) -> Dict[str, Any]:
        """Run a single test file"""
        start_time = time.time()
        
        # Run pytest with JSON output
        json_output = self.output_dir / f"{Path(test_file).stem}_result.json"
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--json-report",
            f"--json-report-file={json_output}",
            "--tb=short"
        ]
        
        # Set environment for headless testing
        env = os.environ.copy()
        env['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Run the test
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env
        )
        
        duration = time.time() - start_time
        
        # Parse results
        test_result = {
            'file': test_file,
            'duration': duration,
            'return_code': process.returncode,
            'stdout': process.stdout,
            'stderr': process.stderr
        }
        
        # Try to load JSON report
        if json_output.exists():
            try:
                with open(json_output, 'r') as f:
                    test_result['pytest_report'] = json.load(f)
            except:
                test_result['pytest_report'] = None
                
        return test_result
        
    def calculate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate test summary statistics"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_duration = 0
        
        for result in results:
            total_duration += result['duration']
            
            if result.get('pytest_report'):
                report = result['pytest_report']
                summary = report.get('summary', {})
                total_tests += summary.get('total', 0)
                passed_tests += summary.get('passed', 0)
                failed_tests += summary.get('failed', 0)
                skipped_tests += summary.get('skipped', 0)
                
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration
        }
        
    def generate_html_report(self, suite_results: Dict[str, Any]) -> Path:
        """Generate HTML test report"""
        report_path = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .test-detail {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        pre {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: #28a745;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Excel Macro Automation - Test Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="stat-card">
                <h3>Total Tests</h3>
                <div class="value">{suite_results['summary']['total_tests']}</div>
            </div>
            <div class="stat-card">
                <h3>Passed</h3>
                <div class="value success">{suite_results['summary']['passed_tests']}</div>
            </div>
            <div class="stat-card">
                <h3>Failed</h3>
                <div class="value failure">{suite_results['summary']['failed_tests']}</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">{suite_results['summary']['success_rate']:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Duration</h3>
                <div class="value">{suite_results['summary']['total_duration']:.1f}s</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {suite_results['summary']['success_rate']}%">
                {suite_results['summary']['success_rate']:.1f}%
            </div>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test File</th>
                    <th>Total</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Duration</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add test results
        for result in suite_results['results']:
            if result.get('pytest_report'):
                report = result['pytest_report'].get('summary', {})
                # Handle different report formats
                failed = report.get('failed', 0)
                if 'passed' in report and 'total' in report:
                    # Calculate failed from total - passed if not present
                    if 'failed' not in report:
                        failed = report['total'] - report['passed']
                status = "✅ Pass" if failed == 0 else "❌ Fail"
                status_class = "success" if failed == 0 else "failure"
            else:
                report = {'total': 0, 'passed': 0, 'failed': 0}
                status = "⚠️ Error"
                status_class = "warning"
                
            html_content += f"""
                <tr>
                    <td>{Path(result['file']).name}</td>
                    <td>{report.get('total', 0)}</td>
                    <td>{report.get('passed', 0)}</td>
                    <td>{failed}</td>
                    <td>{result['duration']:.2f}s</td>
                    <td class="{status_class}">{status}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
        
        <h2>Detailed Results</h2>
"""
        
        # Add detailed results for failed tests
        for result in suite_results['results']:
            if result.get('pytest_report'):
                summary = result['pytest_report'].get('summary', {})
                failed = summary.get('failed', summary.get('total', 0) - summary.get('passed', 0))
                if failed > 0:
                    html_content += f"""
        <div class="test-detail">
            <h3>{Path(result['file']).name}</h3>
            <h4>Failed Tests:</h4>
            <pre>{self._extract_failures(result['pytest_report'])}</pre>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
        
    def _extract_failures(self, pytest_report: Dict) -> str:
        """Extract failure information from pytest report"""
        failures = []
        
        for test in pytest_report.get('tests', []):
            if test['outcome'] == 'failed':
                failures.append(f"Test: {test['nodeid']}")
                if 'call' in test and 'longrepr' in test['call']:
                    failures.append(f"Error: {test['call']['longrepr']}")
                failures.append("-" * 60)
                
        return "\n".join(failures)
        
    def generate_csv_report(self, suite_results: Dict[str, Any]) -> Path:
        """Generate CSV test report"""
        report_path = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Prepare data for CSV
        rows = []
        for result in suite_results['results']:
            if result.get('pytest_report'):
                for test in result['pytest_report'].get('tests', []):
                    rows.append({
                        'file': Path(result['file']).name,
                        'test_name': test['nodeid'],
                        'outcome': test['outcome'],
                        'duration': test.get('duration', 0),
                        'timestamp': datetime.now().isoformat()
                    })
                    
        # Create DataFrame and save
        df = pd.DataFrame(rows)
        df.to_csv(report_path, index=False)
        
        return report_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run automated tests for Excel Macro Automation")
    parser.add_argument(
        '--tests', 
        nargs='+',
        help='Specific test files to run',
        default=None
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for test results',
        default='test_results'
    )
    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Skip CSV report generation'
    )
    
    args = parser.parse_args()
    
    # Default test files if none specified
    if args.tests is None:
        test_dir = Path(__file__).parent / "tests" / "integration"
        args.tests = [
            str(test_dir / "test_drag_drop_integration.py"),
            str(test_dir / "test_step_configuration.py"),
            str(test_dir / "test_execution_logging.py")
        ]
    
    # Create runner
    runner = TestRunner(args.output_dir)
    
    print("Excel Macro Automation - Automated Test Runner")
    print("=" * 60)
    print(f"Running tests: {len(args.tests)} test files")
    print(f"Output directory: {runner.output_dir}")
    print("=" * 60)
    
    # Run tests
    results = runner.run_test_suite(args.tests)
    
    # Generate reports
    reports = []
    
    if not args.no_html:
        html_report = runner.generate_html_report(results)
        reports.append(('HTML', html_report))
        print(f"\n✅ HTML report generated: {html_report}")
        
    if not args.no_csv:
        csv_report = runner.generate_csv_report(results)
        reports.append(('CSV', csv_report))
        print(f"✅ CSV report generated: {csv_report}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed_tests']}")
    print(f"Failed: {results['summary']['failed_tests']}")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Total Duration: {results['summary']['total_duration']:.1f} seconds")
    print("=" * 60)
    
    # Return exit code based on test results
    return 0 if results['summary']['failed_tests'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())