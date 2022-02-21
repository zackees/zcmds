import os

SELF_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(SELF_DIR, "..", ".."))
BIN_DIR = os.path.join(BASE_DIR, "bin")

assert os.path.exists(BIN_DIR), f"could not find {BIN_DIR}"


def main():
    cmds = os.listdir(BIN_DIR)
    cmds.append("ytclip")
    cmds.sort()
    print("\n".join(cmds))
    return


if __name__ == "__main__":
    main()
