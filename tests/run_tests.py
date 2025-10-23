#!/usr/bin/env python3
"""
Test runner for Stitch Shield Integration tests.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_unit_tests():
    """Run unit tests with mocked AWS services."""
    print("Running unit tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_presigned_upload.py::TestPresignedURLGeneration',
        'test_shield_integration.py::TestShieldIntegration',
        '-v', '--tb=short'
    ]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_integration_tests():
    """Run integration tests against actual AWS services."""
    print("Running integration tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_presigned_upload.py::TestPresignedUpload',
        'test_shield_integration.py::TestShieldIntegrationEndToEnd',
        '-v', '--tb=short'
    ]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        '.',
        '-v', '--tb=short'
    ]
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def main():
    parser = argparse.ArgumentParser(description='Run Stitch Shield Integration tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.unit:
        result = run_unit_tests()
    elif args.integration:
        result = run_integration_tests()
    elif args.all:
        result = run_all_tests()
    else:
        print("Please specify --unit, --integration, or --all")
        return 1
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
