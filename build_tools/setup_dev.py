#!/usr/bin/env python3
"""
Development setup script for Top 10 Pony Voting Processing

This script helps developers set up their development environment.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Setting up Top 10 Pony Voting Processing development environment...")
    
    # Check if Poetry is installed
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✓ Poetry is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Poetry is not installed. Please install Poetry first:")
        print("  Visit: https://python-poetry.org/docs/#installation")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("poetry install", "Installing dependencies"):
        sys.exit(1)
    
    # Run tests to verify setup
    if not run_command("poetry run python test.py", "Running tests"):
        print("⚠ Tests failed, but environment is set up. You may need to investigate test failures.")
    
    print("\n🎉 Development environment setup complete!")
    print("\nUseful commands:")
    print("  poetry run python main.py    # Run the main application")
    print("  poetry run python test.py    # Run tests")
    print("  poetry shell                 # Activate virtual environment")
    print("  poetry add <package>         # Add a new dependency")
    print("  poetry add --group dev <pkg> # Add a development dependency")

if __name__ == "__main__":
    main()
