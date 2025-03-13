import importlib
import pkg_resources
import pandas as pd

# List of libraries to check
libraries = [
    "datetime",
    "dotenv",
    "pandas",
    "os",
    "tzlocal",
    "json",
    "praw",
    "time",
    "prawcore",
    "torch",
    "transformers",
    "bertopic",
    "umap-learn",
    "hdbscan",
    "sentence-transformers",
    "tkinter",
    "tkcalendar"
]

def get_library_version(lib_name):
    """
    Check and return the version of a given library.
    If the library is built-in (like datetime, os, time), it returns 'Built-in'.
    If the library is not installed, it returns 'Not Installed'.
    """
    built_in_modules = {"datetime", "os", "json", "time"}

    if lib_name in built_in_modules:
        return "Built-in"

    try:
        return pkg_resources.get_distribution(lib_name).version
    except pkg_resources.DistributionNotFound:
        return "Not Installed"
    except Exception as e:
        return f"Error: {str(e)}"

# Check versions for all libraries
library_versions = {lib: get_library_version(lib) for lib in libraries}

# Display the results
df = pd.DataFrame(library_versions.items(), columns=["Library", "Version"])
print(df)

