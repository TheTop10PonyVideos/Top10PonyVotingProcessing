import subprocess, sys, os, pkg_resources
from functions.messages import suc, inf

def check_install_dependencies():
    inf("Checking for dependency updates...")
    with open("requirements.txt") as f:
        requirements = list(pkg_resources.parse_requirements(f))

    installed = {pkg.key: pkg for pkg in pkg_resources.working_set}

    need_updating = False

    for requirement in requirements:
        package = requirement.key
        if package not in installed:
            need_updating = True
            break
        if requirement.specifier and installed[package].parsed_version not in requirement.specifier:
            need_updating = True
            break
    
    if need_updating:
        inf("Updating...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"])
        os.execv(sys.executable, [sys.executable, sys.argv[0]])
    else:
        suc("All dependencies up to date")
