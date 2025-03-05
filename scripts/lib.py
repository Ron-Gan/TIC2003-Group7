import sys
import subprocess

# List of required packages
packages = [
    "tkinter",
    "tkcalendar",
    "praw",
    "pandas",
    "bertopic",
    "sentence-transformers",
    "torch",
    "transformers",
    "dotenv"
]

# Function to install missing packages
def install_packages(packages):
    for package in packages:
        try:
            __import__(package.replace("-", "_"))  # Convert to importable format
            print(f"{package} is already installed.")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages(packages)