import os

HERE = os.path.dirname(os.path.abspath(__file__))


def get_cmds() -> list[str]:
    cmds_txt = os.path.join(HERE, "cmds.txt")
    with open(cmds_txt, encoding="utf-8", mode="r") as cmds_file:
        cmds = cmds_file.readlines()
    cmds = [cmd.replace('"', "").strip() for cmd in cmds]
    return cmds


if __name__ == "__main__":
    print(get_cmds())
