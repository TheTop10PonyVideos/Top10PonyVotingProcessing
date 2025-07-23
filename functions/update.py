import subprocess, sys, os, pkg_resources
from functions.messages import suc, inf

def check_install_dependencies():
    """Checks if any dependencies in requirements.txt are not installed or if any installed ones don't match the
    specified version. Installs these automatically and restarts the program"""

    inf("Checking for dependency updates...")
    with open("requirements.txt") as f:
        requirements = list(pkg_resources.parse_requirements(f))

    installed = {pkg.key: pkg for pkg in pkg_resources.working_set}

    # packages to install if missing or if there's a version mismatch
    to_install = [
        str(req) for req in requirements
        if req.key not in installed or (req.specifier and installed[req.key].parsed_version not in req.specifier)
    ]
    
    # If there are packages to install, this installs them and restarts the program
    if len(to_install):
        inf("Updating...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + to_install)
        os.execv(sys.executable, [sys.executable, sys.argv[0]])
    else:
        suc("All dependencies up to date")
