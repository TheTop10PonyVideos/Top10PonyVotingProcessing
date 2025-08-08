#!/usr/bin/env python3
"""
Top 10 Pony Voting Processing - Automated Setup and Launcher
===========================================================

This script automatically:
1. Checks for and installs Git, Python 3.13.5, and Poetry if needed
2. Clones or updates the repository from GitHub
3. Sets up the virtual environment with Poetry
4. Launches the application

Usage: python build_exe.py
"""

import os
import sys
import subprocess
import urllib.request
import json
import tempfile
import shutil
import platform
import time
from pathlib import Path

# Configuration
REPO_URL = "https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing"
REPO_NAME = "Top10PonyVotingProcessing"
PYTHON_VERSION = "3.13.5"
APP_DIR = Path.home() / "Top10PonyVotingApp"

class Colors:
    """ANSI color codes for colored output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED
    }
    color = colors.get(status, Colors.BLUE)
    print(f"{color}[{status.upper()}]{Colors.END} {message}")

def run_command(command, description, check=True, capture_output=False, shell=True):
    """Run a command with error handling and status reporting"""
    print_status(f"Running: {description}", "info")
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result
        else:
            result = subprocess.run(command, shell=shell, check=check)
            return result
    except subprocess.CalledProcessError as e:
        print_status(f"Failed: {description}", "error")
        if capture_output and e.stderr:
            print(f"Error output: {e.stderr}")
        return None
    except FileNotFoundError:
        print_status(f"Command not found: {command}", "error")
        return None

def check_command_exists(command):
    """Check if a command exists in the system PATH"""
    try:
        # Try different ways to find the command
        if command == "poetry":
            # Check common Poetry locations
            poetry_locations = [
                "poetry",
                str(Path.home() / ".local" / "bin" / "poetry.exe"),
                str(Path.home() / ".local" / "bin" / "poetry"),
                str(Path.home() / "AppData" / "Roaming" / "Python" / "Scripts" / "poetry.exe"),
            ]
            
            for poetry_path in poetry_locations:
                try:
                    result = subprocess.run([poetry_path, "--version"], 
                                          capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        print_status(f"Found Poetry at: {poetry_path}", "info")
                        return True
                except (FileNotFoundError, OSError):
                    continue
            return False
        else:
            result = subprocess.run([command, "--version"], 
                                  capture_output=True, text=True, check=False)
            return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False

def check_python_version():
    """Check if Python 3.13.5 is installed"""
    # If running as compiled executable, skip Python check since we're already running
    if getattr(sys, 'frozen', False):
        print_status("Running as compiled executable - Python check skipped", "info")
        return True
    
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip().split()[1]
        print_status(f"Found Python {version}", "info")
        
        # Check if it's 3.13.x (we'll accept any 3.13.x version)
        major, minor = version.split('.')[:2]
        if major == "3" and minor == "13":
            print_status("Python 3.13.x is available", "success")
            return True
        else:
            print_status(f"Python {version} found, but 3.13.x is required", "warning")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        print_status("No Python installation found", "warning")
        return False

def install_git():
    """Install Git for Windows"""
    print_status("Installing Git for Windows...", "info")
    
    # Download Git installer
    git_url = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.45.2-64-bit.exe"
    temp_dir = tempfile.mkdtemp()
    git_installer = os.path.join(temp_dir, "git-installer.exe")
    
    try:
        print_status("Downloading Git installer...", "info")
        urllib.request.urlretrieve(git_url, git_installer)
        
        print_status("Running Git installer...", "info")
        # Run installer silently
        result = subprocess.run([git_installer, "/VERYSILENT", "/NORESTART"], 
                              check=True)
        
        print_status("Git installation completed", "success")
        
        # Add Git to PATH for current session
        git_path = r"C:\Program Files\Git\bin"
        if git_path not in os.environ["PATH"]:
            os.environ["PATH"] = f"{git_path};{os.environ['PATH']}"
        
        return True
    except Exception as e:
        print_status(f"Failed to install Git: {e}", "error")
        return False
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def install_python():
    """Install Python 3.13.5"""
    print_status("Installing Python 3.13.5...", "info")
    
    # Download Python installer
    python_url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
    temp_dir = tempfile.mkdtemp()
    python_installer = os.path.join(temp_dir, "python-installer.exe")
    
    try:
        print_status("Downloading Python installer...", "info")
        urllib.request.urlretrieve(python_url, python_installer)
        
        print_status("Running Python installer...", "info")
        # Install Python with specific options
        result = subprocess.run([
            python_installer, 
            "/quiet", 
            "InstallAllUsers=1", 
            "PrependPath=1",
            "Include_test=0"
        ], check=True)
        
        print_status("Python installation completed", "success")
        print_status("Please restart this script to use the newly installed Python", "warning")
        return True
    except Exception as e:
        print_status(f"Failed to install Python: {e}", "error")
        return False
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def install_poetry():
    """Install Poetry"""
    print_status("Installing Poetry...", "info")
    
    try:
        # Download and run Poetry installer
        poetry_url = "https://install.python-poetry.org"
        
        # Use PowerShell to download and run Poetry installer
        command = f'(Invoke-WebRequest -Uri {poetry_url} -UseBasicParsing).Content | python -'
        result = subprocess.run(["powershell", "-Command", command], 
                              check=True, capture_output=True, text=True)
        
        print_status("Poetry installation completed", "success")
        
        # Add Poetry to PATH for current session
        poetry_path = Path.home() / ".local" / "bin"
        if str(poetry_path) not in os.environ["PATH"]:
            os.environ["PATH"] = f"{poetry_path};{os.environ['PATH']}"
        
        return True
    except Exception as e:
        print_status(f"Failed to install Poetry: {e}", "error")
        print_status("Trying alternative Poetry installation method...", "info")
        
        try:
            # Alternative: use pip to install poetry
            result = subprocess.run([sys.executable, "-m", "pip", "install", "poetry"], 
                                  check=True)
            print_status("Poetry installed via pip", "success")
            return True
        except Exception as e2:
            print_status(f"Alternative Poetry installation also failed: {e2}", "error")
            return False

def clone_or_update_repo():
    """Clone repository or update if it exists"""
    if APP_DIR.exists():
        print_status(f"Repository directory exists at {APP_DIR}", "info")
        
        # Check if it's a git repository
        if (APP_DIR / ".git").exists():
            print_status("Updating existing repository...", "info")
            os.chdir(APP_DIR)
            
            # Fetch latest changes
            result = run_command("git fetch origin", "Fetching latest changes")
            if result is None:
                return False
                
            # Reset to latest main/master branch
            branches = ["main", "master", "overhaul_2"]
            for branch in branches:
                result = run_command(f"git checkout {branch}", 
                                   f"Checking out {branch}", check=False)
                if result and result.returncode == 0:
                    run_command("git reset --hard origin/" + branch, 
                              f"Updating to latest {branch}")
                    break
            
            print_status("Repository updated successfully", "success")
            return True
        else:
            print_status("Directory exists but is not a git repository. Removing...", "warning")
            shutil.rmtree(APP_DIR)
    
    # Clone the repository
    print_status(f"Cloning repository to {APP_DIR}...", "info")
    APP_DIR.parent.mkdir(parents=True, exist_ok=True)
    
    result = run_command(f"git clone {REPO_URL} {APP_DIR}", "Cloning repository")
    if result is None:
        return False
    
    print_status("Repository cloned successfully", "success")
    return True

def setup_poetry_environment():
    """Set up Poetry virtual environment and install dependencies"""
    print_status("Setting up Poetry environment...", "info")
    
    # Change to repository directory
    os.chdir(APP_DIR)
    
    # Configure Poetry to create venv in project directory
    run_command("poetry config virtualenvs.in-project true", 
                "Configuring Poetry virtual environment location")
    
    # Install dependencies
    result = run_command("poetry install", "Installing dependencies with Poetry")
    if result is None:
        return False
    
    print_status("Poetry environment setup completed", "success")
    return True

def launch_application():
    """Launch the application"""
    print_status("Launching Top 10 Pony Voting Processing application...", "info")
    
    os.chdir(APP_DIR)
    
    # Launch the application
    result = run_command("poetry run python main.py", "Starting application", check=False)
    
    print_status("Application launched", "success")
    return True

def main():
    """Main setup and launch function"""
    try:
        print_status("Top 10 Pony Voting Processing - Automated Setup", "info")
        print_status("=" * 60, "info")
        
        # Debug info
        if getattr(sys, 'frozen', False):
            print_status("Running as compiled executable", "info")
        else:
            print_status("Running as Python script", "info")
        
        # Check system requirements
        if platform.system() != "Windows":
            print_status("This installer is designed for Windows systems only", "error")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print_status("Windows system detected - continuing...", "info")
        
        # Check and install Git
        print_status("Checking Git installation...", "info")
        if check_command_exists("git"):
            print_status("Git is already installed", "success")
        else:
            print_status("Git not found. Installing...", "warning")
            if not install_git():
                print_status("Failed to install Git. Please install manually.", "error")
                input("Press Enter to exit...")
                sys.exit(1)
        
        # Check and install Python
        print_status("Checking Python installation...", "info")
        if check_python_version():
            print_status("Compatible Python version found", "success")
        else:
            print_status("Python 3.13.x not found. Installing...", "warning")
            if not install_python():
                print_status("Failed to install Python. Please install manually.", "error")
                input("Press Enter to exit...")
                sys.exit(1)
            else:
                print_status("Python installed. Please restart this script.", "warning")
                input("Press Enter to exit...")
                sys.exit(0)
        
        # Check and install Poetry
        print_status("Checking Poetry installation...", "info")
        if check_command_exists("poetry"):
            print_status("Poetry is already installed", "success")
        else:
            print_status("Poetry not found. Installing...", "warning")
            if not install_poetry():
                print_status("Failed to install Poetry. Please install manually.", "error")
                input("Press Enter to exit...")
                sys.exit(1)
        
        # Clone or update repository
        print_status("Setting up repository...", "info")
        if not clone_or_update_repo():
            print_status("Failed to set up repository", "error")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Setup Poetry environment
        print_status("Setting up Poetry environment...", "info")
        if not setup_poetry_environment():
            print_status("Failed to set up Poetry environment", "error")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Launch application
        print_status("Setup completed successfully!", "success")
        print_status("Launching application...", "info")
        
        # Give user a moment to read the messages
        time.sleep(2)
        
        if not launch_application():
            print_status("Failed to launch application", "error")
            input("Press Enter to exit...")
            sys.exit(1)
            
    except Exception as e:
        print_status(f"Critical error in main function: {e}", "error")
        print_status(f"Error type: {type(e).__name__}", "error")
        import traceback
        print_status(f"Traceback: {traceback.format_exc()}", "error")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Top 10 Pony Voting Processing - Debug Info")
        print("=" * 60)
        print(f"Python executable: {sys.executable}")
        print(f"Frozen (compiled): {getattr(sys, 'frozen', False)}")
        print(f"Platform: {platform.system()}")
        print(f"Working directory: {os.getcwd()}")
        print("=" * 60)
        
        main()
    except KeyboardInterrupt:
        print_status("\nSetup cancelled by user", "warning")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        import traceback
        print_status(f"Full traceback: {traceback.format_exc()}", "error")
        input("Press Enter to exit...")
        sys.exit(1)
