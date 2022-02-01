
import os
import sys
import shutil
import json
import subprocess
import tempfile
import winreg

SELF_DIR = os.path.dirname(__file__)
COMMON_DIR = os.path.join(SELF_DIR, '..', 'common')
OUT_CMD_DIR = os.path.abspath(os.path.join(SELF_DIR, '..', '..', '..', 'cmds'))

sys.path.insert(0, os.path.abspath(SELF_DIR))
import _path_manip

def gen_win_cmds():
    common_cmds = [os.path.abspath(os.path.join(COMMON_DIR, f))
                   for f in os.listdir(COMMON_DIR)]
    macos_cmds = [os.path.abspath(os.path.join(SELF_DIR, f))
                  for f in os.listdir(SELF_DIR)]
    all_cmds = common_cmds + macos_cmds
    all_cmds = [cmd for cmd in all_cmds if not os.path.basename(
        cmd).startswith('_') and cmd.endswith(".py")]
    shutil.rmtree(OUT_CMD_DIR, ignore_errors=True)
    os.makedirs(OUT_CMD_DIR, exist_ok=True)
    cmd_set = set([])
    for cmd in all_cmds:
        if cmd in cmd_set:
            sys.stderr.write(
                f"Warning, duplicate found for {os.path.basename(cmd)}, skipping.")
            continue
        else:
            cmd_set.add(cmd)
        print("making command for " + cmd)
        cmd_name = os.path.basename(cmd)
        out_cmd = os.path.join(OUT_CMD_DIR, cmd_name)[
            0:-3] + '.bat'  # swap .py -> .bat
        with open(out_cmd, 'wt') as f:
            f.write(f"python {cmd} %1 %2 %3 %4 %5 %6\n")

def is_cmd_path_installed():
    all_paths = _path_manip.read_user_path()
    print(all_paths)
    return OUT_CMD_DIR in all_paths

def add_cmds_to_path():
    if is_cmd_path_installed():
        print(f'Already found {OUT_CMD_DIR} in %PATH%')
        return
    print(f'Did not found {OUT_CMD_DIR} in %PATH%, adding...')
    _path_manip.add_user_path(OUT_CMD_DIR)


def main():
    gen_win_cmds()
    add_cmds_to_path()
