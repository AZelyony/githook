import os
import platform
import subprocess
import sys
import urllib.request
import tarfile
import json
import shutil
import zipfile


def install_gitleaks_linux():
    print("Installing gitleaks on Linux...")
    response = urllib.request.urlopen("https://api.github.com/repos/gitleaks/gitleaks/releases/latest")
    data = json.load(response)
    gitleaks_version = data['tag_name'].lstrip('v')
    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{gitleaks_version}/gitleaks_{gitleaks_version}_linux_x64.tar.gz"
    filedata = urllib.request.urlopen(url)
    with tarfile.open(fileobj=filedata, mode="r:gz") as tar:
        tar.extract("gitleaks")
    try:
        shutil.move("gitleaks", "/usr/local/bin/gitleaks")
        os.chmod("/usr/local/bin/gitleaks", 0o755)
        print(f"Gitleaks {gitleaks_version} installed successfully.")
    except PermissionError:
        print("Error: Permission denied. Please run the script with sudo.")
        sys.exit(1)

def install_gitleaks_macos():
    try:
        subprocess.run(["brew", "install", "gitleaks"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Installation failed. Please ensure Homebrew is installed and try again.")
        sys.exit(1)

def install_gitleaks_windows():
    print("Installing gitleaks on Windows...")
    response = urllib.request.urlopen("https://api.github.com/repos/gitleaks/gitleaks/releases/latest")
    data = json.load(response)
    gitleaks_version = data['tag_name'].lstrip('v')
    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{gitleaks_version}/gitleaks_{gitleaks_version}_windows_x64.zip"
    filedata = urllib.request.urlopen(url)
    zip_path = "gitleaks.zip"
    with open(zip_path, "wb") as f:
        f.write(filedata.read())
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
    os.remove(zip_path)
    try:
        shutil.move("gitleaks.exe", "C:\\Program Files\\gitleaks\\gitleaks.exe")
        subprocess.run(["setx", "PATH", "%PATH%;C:\\Program Files\\gitleaks"], check=True)
        print(f"Gitleaks {gitleaks_version} installed successfully.")
    except PermissionError:
        print("Error: Permission denied. Please run the script as Administrator.")
        sys.exit(1)

def check_gitleaks_installed():
    try:
        subprocess.run(["gitleaks", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Gitleaks is installed.")
        return True
    except subprocess.CalledProcessError:
        print("Gitleaks is not installed.")
        return False

def install_gitleaks():
    system = platform.system()
    if system == "Linux":
        install_gitleaks_linux()
    elif system == "Darwin":
        install_gitleaks_macos()
    elif system == "Windows":
        install_gitleaks_windows()
    else:
        print("Unsupported operating system.")
        sys.exit(1)

def manage_pre_commit_hook(enable):
    hooks_dir = os.path.join(".git", "hooks")
    pre_commit_script = os.path.join(hooks_dir, "pre-commit")
    script_path = os.path.abspath(__file__)
    
    if enable:
        if not os.path.exists(pre_commit_script):
            shutil.copy(script_path, pre_commit_script)
            os.chmod(pre_commit_script, 0o755)
            print("Gitleaks pre-commit hook enabled.")

def main():
    try:
        enabled = subprocess.run(
            ["git", "config", "--get", "hooks.gitleaks.enabled"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode().strip()
    except subprocess.CalledProcessError:
        enabled = None

    if enabled is None: #maybe first run, then install
        subprocess.run(["git", "config", "--local", "hooks.gitleaks.enabled", "true"], check=True)
        enabled = "true"
        manage_pre_commit_hook(enable=True)
        print("Gitleaks has been enabled and pre-commit hook has been installed.")
        sys.exit(0)

    if enabled.lower() == "true":
        if not check_gitleaks_installed():
            install_gitleaks()
            manage_pre_commit_hook(enable=True)
        
        command = ["gitleaks", "protect", "--redact=25", "-v", "--staged"]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stderr)
        print(result.stdout)        

        if result.returncode == 0:
            print("No secrets detected. Commit allowed.")
            sys.exit(0)
        else:
            print("Warning: gitleaks has detected sensitive information in your changes. Commit aborted.")
            print("To disable the gitleaks precommit hook run the following command:")
            print("git config --local --bool hooks.gitleaks.enabled false")
            sys.exit(1)
    else:
        print("Gitleaks is disabled via git config.")
        print("You can enable Gitleaks with the following command:")
        print("git config --local --bool hooks.gitleaks.enabled true")
        sys.exit(0)

if __name__ == "__main__":
    main()
