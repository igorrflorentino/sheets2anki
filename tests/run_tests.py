#!/usr/bin/env python3
"""
Script to run all Sheets2Anki tests

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Unit tests only
    python run_tests.py --integration # Integration tests only
    python run_tests.py --coverage   # With coverage report
    python run_tests.py --verbose    # Detailed output
    python run_tests.py --fast       # Skip slow tests
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run Sheets2Anki tests")

    parser.add_argument(
        "--unit", action="store_true", help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--fast", action="store_true", help="Skip tests marked as slow"
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Run specific test file"
    )
    parser.add_argument(
        "--function", "-k", type=str, help="Run specific test function"
    )

    args = parser.parse_args()

    # Ensure we are in the correct directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add flags based on arguments
    if args.verbose:
        cmd.extend(["-v", "-s"])

    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    if args.fast:
        cmd.extend(["-m", "not slow"])

    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])

    if args.file:
        test_file = Path("tests") / args.file
        if not test_file.suffix:
            test_file = test_file.with_suffix(".py")
        if not str(test_file).startswith("test_"):
            test_file = test_file.parent / f"test_{test_file.name}"
        cmd.append(str(test_file))
    else:
        cmd.append("tests/")

    if args.function:
        cmd.extend(["-k", args.function])

    # Default pytest settings
    cmd.extend(
        [
            "--tb=short",  # Short traceback
            "--strict-markers",  # Strict markers
            "--disable-warnings",  # Disable verbose warnings
        ]
    )

    print(f"🧪 Running tests with command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        # Run tests
        result = subprocess.run(cmd, check=False)

        # Final report
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")

            if args.coverage:
                print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("❌ Some tests failed!")

        return result.returncode

    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return 1


def show_test_info():
    """Show information about available tests."""
    print("📋 Available Tests:")
    print("-" * 40)

    test_files = [
        ("test_data_processor.py", "TSV data processing"),
        ("test_config_manager.py", "Settings management"),
        ("test_utils.py", "Utility functions"),
        ("test_student_manager.py", "Student management"),
        ("test_integration.py", "Integration tests"),
        ("test_new_tags.py", "Tag system (existing)"),
    ]

    for filename, description in test_files:
        test_path = Path("tests") / filename
        status = "✅" if test_path.exists() else "❌"
        print(f"{status} {filename:25} - {description}")

    print("\n📊 Statistics:")
    print(f"Total test files: {len(test_files)}")

    existing_files = [f for f, _ in test_files if (Path("tests") / f).exists()]
    print(f"Existing files: {len(existing_files)}")

    print("\n🏃 Usage examples:")
    print("  python run_tests.py --unit --verbose")
    print("  python run_tests.py --integration --coverage")
    print("  python run_tests.py --file data_processor --verbose")
    print("  python run_tests.py --function test_parse_students --verbose")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_test_info()
    else:
        sys.exit(main())
