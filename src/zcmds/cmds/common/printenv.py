"""
Prints the environment variables
"""

import os
import sys


def main():
    """Prints the environment variables"""
    # Copy the environment variables to a new dictionary
    env = os.environ.copy()
    # Remove the path variable
    env.pop("PATH", None)
    for key, val in env.items():
        print(f"  {key} = {val}")
    print("Path:")
    for path in sys.path:
        print(f"  {path}")
    sys.exit(0)
