#!/usr/bin/env python3
"""
Create Installer EXEs - PyInstaller Build Script
===============================================

This script uses PyInstaller to create two standalone .exe files:
1. User/Production build - pulls from main branch
2. Development build - pulls from overhaul_2 branch

Both executables will:
1. Install Git, Python 3.13.5, and Poetry (if not present)
2. Clone/update the Top10PonyVotingProcessing repository
3. Set up Poetry virtual environment and dependencies
4. Launch the application

Usage: python create_installer_exe.py
Output: 
  - dist/Top10PonyVotingSetup-User.exe (Production)
  - dist/Top10PonyVotingSetup-Dev.exe (Development)
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil
import datetime

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True, text=True)
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            return False

def check_build_file():
    """Check if build_exe.py exists"""
    if not Path("build_exe.py").exists():
        print("✗ build_exe.py not found in current directory")
        print("Make sure you're running this script from the project root")
        return False
    print("✓ Found build_exe.py")
    return True

def create_dev_version():
    """Create a development version of build_exe.py that pulls from overhaul_2 branch"""
    print("Creating development version...")
    
    # Read the original build_exe.py
    with open("build_exe.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Modify for development version
    dev_content = content.replace(
        'REPO_URL = "https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing"',
        'REPO_URL = "https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing.git"'
    )
    
    # Update the clone_or_update_repo function to prioritize overhaul_2 branch
    dev_content = dev_content.replace(
        'branches = ["main", "master", "overhaul_2"]',
        'branches = ["overhaul_2", "main", "master"]'
    )
    
    # Update clone command to specify overhaul_2 branch
    dev_content = dev_content.replace(
        'result = run_command(f"git clone {REPO_URL} {APP_DIR}", "Cloning repository")',
        'result = run_command(f"git clone -b overhaul_2 {REPO_URL} {APP_DIR}", "Cloning development repository (overhaul_2 branch)")'
    )
    
    # Update the window title and messages to indicate it's the dev version
    dev_content = dev_content.replace(
        'print_status("Top 10 Pony Voting Processing - Automated Setup", "info")',
        'print_status("Top 10 Pony Voting Processing - Development Build Setup", "info")'
    )
    
    # Write the development version
    with open("build_exe_dev.py", "w", encoding="utf-8") as f:
        f.write(dev_content)
    
    print("✓ Development version created as build_exe_dev.py")
    return True

def create_version_info(build_type):
    """Create version info file for the executable"""
    description = f"Top 10 Pony Voting Processing - Automated Installer ({build_type})"
    filename = f"Top10PonyVotingSetup-{build_type}.exe"
    
    version_info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
filevers=(1,0,0,0),
prodvers=(1,0,0,0),
mask=0x3f,
flags=0x0,
OS=0x4,
fileType=0x1,
subtype=0x0,
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'TheTop10PonyVideos'),
    StringStruct(u'FileDescription', u'{description}'),
    StringStruct(u'FileVersion', u'1.0.0.0'),
    StringStruct(u'InternalName', u'Top10PonyVotingSetup-{build_type}'),
    StringStruct(u'LegalCopyright', u'© TheTop10PonyVideos'),
    StringStruct(u'OriginalFilename', u'{filename}'),
    StringStruct(u'ProductName', u'Top 10 Pony Voting Processing Installer'),
    StringStruct(u'ProductVersion', u'1.0.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    version_file = f"version_info_{build_type.lower()}.txt"
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(version_info)
    print(f"✓ Created version info file for {build_type} build")
    return version_file

def build_executable(script_name, exe_name, build_type, description):
    """Build a standalone executable using PyInstaller"""
    
    print(f"\n{'='*60}")
    print(f"Building {description}")
    print(f"{'='*60}")
    
    # Create version info for this build
    version_file = create_version_info(build_type)
    
    # Prepare PyInstaller command
    icon_path = Path("images/icon.ico")
    icon_option = ["--icon", str(icon_path)] if icon_path.exists() else []
    
    command = [
        "pyinstaller",
        "--onefile",                           # Create single executable
        "--console",                           # Keep console window for user feedback
        f"--name={exe_name}",                  # Executable name
        "--distpath=dist",                     # Output directory
        "--workpath=build",                    # Build directory
        "--specpath=.",                        # Spec file location
        f"--version-file={version_file}",      # Version information
        "--clean",                             # Clean cache
        "--noconfirm",                         # Don't ask for confirmation
        "--hidden-import=urllib.request",      # Ensure urllib.request is included
        "--hidden-import=json",                # Ensure json is included
        "--hidden-import=tempfile",            # Ensure tempfile is included
        "--hidden-import=shutil",              # Ensure shutil is included
        "--hidden-import=pathlib",             # Ensure pathlib is included
        "--collect-all=urllib3",               # Include urllib3 and dependencies
        "--collect-all=certifi",               # Include certificates
        script_name
    ] + icon_option
    
    # Add data files if they exist
    if Path("INSTALLER_README.md").exists():
        command.extend(["--add-data", "INSTALLER_README.md;."])
    
    try:
        print("Building executable with PyInstaller...")
        print("This may take a few minutes...")
        
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Check if the executable was created
        exe_path = Path(f"dist/{exe_name}.exe")
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            print(f"\n✓ {description} CREATED SUCCESSFULLY!")
            print(f"Location: {exe_path.absolute()}")
            print(f"Size: {exe_size:.1f} MB")
            
            return True
        else:
            print(f"✗ {description} not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} build failed with error code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error during {description} build: {e}")
        return False

def create_build_info():
    """Create a text file with build information"""
    build_info = f"""Top 10 Pony Voting Processing - Installer Builds
===============================================

This directory contains two installer executables:

1. Top10PonyVotingSetup-User.exe
   - For end users and production use
   - Pulls from the main/stable branch
   - Production version

2. Top10PonyVotingSetup-Dev.exe
   - For developers and testers
   - Pulls from the overhaul_2 branch
   - Development version with latest features

Both installers will:
- Check for and install Git, Python 3.13.5, and Poetry if needed
- Clone/update the repository from the appropriate branch
- Set up the virtual environment with Poetry
- Install all dependencies
- Launch the application

Usage:
Simply double-click the appropriate .exe file for your needs.
No other software installation required!

Repository: https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing
Build Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Installation Location:
The application will be installed to: %USERPROFILE%\\Top10PonyVotingApp\\

Troubleshooting:
If you encounter issues, see INSTALLER_README.md for detailed troubleshooting steps.
"""
    
    with open("dist/BUILD_INFO.txt", "w", encoding="utf-8") as f:
        f.write(build_info)
    print("✓ Created build information file")

def cleanup_build_files():
    """Clean up temporary build files"""
    print("\nCleaning up build files...")
    
    files_to_remove = [
        "build_exe_dev.py",
        "version_info_user.txt",
        "version_info_dev.txt",
        "Top10PonyVotingSetup-User.spec",
        "Top10PonyVotingSetup-Dev.spec"
    ]
    
    dirs_to_remove = [
        "build"
    ]
    
    # Remove files
    for file_path in files_to_remove:
        try:
            if Path(file_path).exists():
                os.remove(file_path)
                print(f"✓ Removed {file_path}")
        except Exception as e:
            print(f"⚠ Could not remove {file_path}: {e}")
    
    # Remove directories
    for dir_path in dirs_to_remove:
        try:
            if Path(dir_path).exists():
                shutil.rmtree(dir_path)
                print(f"✓ Removed {dir_path}/")
        except Exception as e:
            print(f"⚠ Could not remove {dir_path}: {e}")

def main():
    """Main build function"""
    print("Top 10 Pony Voting Processing - Dual Installer Builder")
    print("This will create both User and Development .exe installers")
    print("=" * 60)
    
    # Check prerequisites
    if not check_build_file():
        sys.exit(1)
    
    if not install_pyinstaller():
        sys.exit(1)
    
    # Create development version of the script
    if not create_dev_version():
        sys.exit(1)
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    success_count = 0
    
    # Build user/production version
    if build_executable("build_exe.py", "Top10PonyVotingSetup-User", "User", "User/Production executable"):
        success_count += 1
    
    # Build development version
    if build_executable("build_exe_dev.py", "Top10PonyVotingSetup-Dev", "Dev", "Development executable"):
        success_count += 1
    
    # Create build info
    if success_count > 0:
        create_build_info()
    
    # Clean up temporary files
    cleanup_build_files()
    
    print(f"\n{'='*60}")
    if success_count == 2:
        print("✓ BOTH EXECUTABLES BUILT SUCCESSFULLY!")
        print("=" * 60)
        print("\nFiles created:")
        print("  📦 dist/Top10PonyVotingSetup-User.exe")
        print("     └─ Production version (main branch)")
        print("  🔧 dist/Top10PonyVotingSetup-Dev.exe")
        print("     └─ Development version (overhaul_2 branch)")
        print("  📄 dist/BUILD_INFO.txt")
        print("     └─ Information and usage guide")
        
        print("\nFeatures included in both executables:")
        print("  • Automatic Git, Python 3.13.5, Poetry installation")
        print("  • Repository cloning/updating")
        print("  • Virtual environment setup")
        print("  • Dependency installation")
        print("  • Application launcher")
        
        print("\nDistribution:")
        print("  • End users: Give them Top10PonyVotingSetup-User.exe")
        print("  • Developers/Testers: Give them Top10PonyVotingSetup-Dev.exe")
        print("  • No other files needed - completely standalone!")
        
    elif success_count == 1:
        print("⚠ PARTIALLY SUCCESSFUL - One executable built")
    else:
        print("✗ BUILD FAILED - No executables created")
        sys.exit(1)
    
    print(f"\n🎉 Build process completed successfully!")
    print("\nNext steps:")
    print("1. Test both installers to ensure they work correctly")
    print("2. Distribute the appropriate .exe to your target users")
    print("3. Users can run the .exe without any prerequisites")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
