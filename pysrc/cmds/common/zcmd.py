import sys
import os

SELF_DIR = os.path.dirname(__file__)
CMD_DIR = os.path.abspath(os.path.join(SELF_DIR, '..', '..', '..', 'cmds'))

def main():
    cmds = os.listdir(CMD_DIR)
    cmds.sort()
    print("\n".join(cmds))
    return


if __name__ == '__main__':
    main()