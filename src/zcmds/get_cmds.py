import os

HERE = os.path.dirname(os.path.abspath(__file__))

EXTRA_COMMANDS = ["transcribe-anything", "aicode", "askai"]


def get_cmds(just_names: bool = False) -> list[str]:
    cmds_txt = os.path.join(HERE, "cmds.txt")
    with open(cmds_txt, encoding="utf-8", mode="r") as cmds_file:
        cmds = cmds_file.readlines()
    cmds = [cmd.replace('"', "").strip() for cmd in cmds]
    if just_names:
        cmds = [cmd.split(" ")[0] for cmd in cmds]
    cmds = cmds + EXTRA_COMMANDS
    cmds = sorted(cmds)
    return cmds


if __name__ == "__main__":
    print(get_cmds())
