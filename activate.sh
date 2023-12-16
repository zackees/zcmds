
#!/bin/bash

# Function that computes absolute path of a file
abs_path() {
  dir=$(dirname "$1")
  (cd "$dir" &>/dev/null && printf "%s/%s" "$PWD" "${1##*/}")
}

# Navigate to the directory where the current script resides
bashfile=$(abs_path "${BASH_SOURCE[0]}")
selfdir=$(dirname "$bashfile")
cd "$selfdir"

if [[ "$IN_ACTIVATED_ENV" == "1" ]]; then
  IN_ACTIVATED_ENV=1
else
  IN_ACTIVATED_ENV=0
fi

# If the 'venv' directory doesn't exist, print a message and exit.
if [[ ! -d "venv" ]]; then
  echo "The 'venv' directory does not exist, creating..."
  if [[ "$IN_ACTIVATED_ENV" == "1" ]]; then
    echo "Cannot install a new environment while in an activated environment. Please launch a new shell and try again."
    exit 1
  fi
  # Check the operating system type.
  # If it is macOS or Linux, then create an alias 'python' for 'python3'
  # and an alias 'pip' for 'pip3'. This is helpful if python2 is the default python in the system.
  echo "OSTYPE: $OSTYPE"
  if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux-gnu"* ]]; then
    python3 install.py
  else
    python install.py
  fi

  . ./venv/bin/activate
  export IN_ACTIVATED_ENV=1
  this_dir=$(pwd)
  export PATH="$this_dir:$PATH"
  echo "Environment created."
  pip install -e .
  exit 0
fi

if [[ "$IN_ACTIVATED_ENV" != "1" ]]; then
  . ./venv/bin/activate
  export IN_ACTIVATED_ENV=1
  this_dir=$(pwd)
  export PATH="$this_dir:$PATH"
fi
