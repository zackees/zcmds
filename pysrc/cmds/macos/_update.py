import os, sys, shutil, json

SELF_DIR = os.path.dirname(__file__)
COMMON_DIR = os.path.join(SELF_DIR, "..", "common")
OUT_CMD_DIR = os.path.abspath(os.path.join(SELF_DIR, "..", "..", "..", "cmds"))


def gen_macos_cmds():
    common_cmds = [
        os.path.abspath(os.path.join(COMMON_DIR, f)) for f in os.listdir(COMMON_DIR)
    ]
    macos_cmds = [
        os.path.abspath(os.path.join(SELF_DIR, f)) for f in os.listdir(SELF_DIR)
    ]
    all_cmds = common_cmds + macos_cmds
    all_cmds = [
        cmd
        for cmd in all_cmds
        if not os.path.basename(cmd).startswith("_") and cmd.endswith(".py")
    ]
    shutil.rmtree(OUT_CMD_DIR, ignore_errors=True)
    os.makedirs(OUT_CMD_DIR, exist_ok=True)
    cmd_set = set([])
    for cmd in all_cmds:
        if cmd in cmd_set:
            sys.stderr.write(
                f"Warning, duplicate found for {os.path.basename(cmd)}, skipping."
            )
            continue
        else:
            cmd_set.add(cmd)
        print("making command for " + cmd)
        cmd_name = os.path.basename(cmd)
        out_cmd = os.path.join(OUT_CMD_DIR, cmd_name)[0:-3]  # strips .py extension
        with open(out_cmd, "wt") as f:
            f.write("python3 " + cmd + "\n")
        # Allow execution on the commands.
        os.system("chmod +x " + out_cmd)


def add_cmds_to_path():
    needle = f"export PATH=$PATH:{OUT_CMD_DIR}"
    bash_profile_file = os.path.expanduser(os.path.join("~", ".bash_profile"))
    with open(bash_profile_file, "rt") as fd:
        bash_profile = fd.read()
    if needle in bash_profile:
        return
    print(f"Attempting to install {OUT_CMD_DIR} in {bash_profile_file}")
    lines = bash_profile.splitlines()
    last_path_line = -1
    for i, line in enumerate(lines):
        if "export PATH=" in line:
            last_path_line = i
            continue
    # print(bash_profile)
    # if needle not in bash_profile:
    #    print("")
    if last_path_line == -1:
        raise ValueError(
            f"Could not find a place to splice in {OUT_CMD_DIR} into {bash_profile_file}, please do it manually."
        )
    lines.insert(last_path_line + 1, needle)
    # print('\n'.join(lines))
    out_file = "\n".join(lines) + "\n"
    with open(bash_profile_file, "wt") as fd:
        fd.write(out_file)

    with open(bash_profile_file, "rt") as fd:
        bash_profile = fd.read()
    if needle not in bash_profile:
        raise ValueError(f"{needle} could not be installed into {bash_profile_file}")


def add_python_key_bindings():
    target_file = os.path.join(
        os.path.expanduser("~"), "Library", "Keybindings", "DefaultKeyBinding.dict"
    )
    src_file = os.path.join(SELF_DIR, "macOS_key_bindings.dict")
    with open(src_file, "rt") as fd:
        src_file_content = fd.read()
    if not os.path.exists(target_file):
        with open(target_file, "rt") as fd:
            fd.write(src_file_content)
            return
    else:
        with open(target_file, "rt") as fd:
            target_file_content = fd.read()
        if target_file_content != src_file_content:
            sys.stderr.write(f"Please manually merge {src_file} with {target_file}\n")


def main():
    gen_macos_cmds()
    add_cmds_to_path()
    add_python_key_bindings()
