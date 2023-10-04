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
    paths = None
    env_items = list(env.items())
    # sort
    env_items = sorted(env_items, key=lambda x: x[0].lower())
    for key, val in env_items:
        if key.lower() == "path":
            paths = val
            continue
        else:
            print(f"{key}={val}")
    print("PATH:")
    for path in paths.split(os.pathsep):
        print(f"  {path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
