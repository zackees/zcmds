import sys
import os

SELF_DIR = os.path.dirname(__file__)

def main():
    if sys.platform == 'darwin':
        target_dir = os.path.abspath(os.path.join(SELF_DIR, '..', 'macos'))
        sys.path.append(target_dir)
        import _update
        _update.main()
        return
    else:
        raise ValueError('Unhandled platform ' + sys.platform)


if __name__ == '__main__':
    main()