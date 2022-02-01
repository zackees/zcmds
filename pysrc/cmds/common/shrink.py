import os
import argparse
import sys
from pathlib import Path

def main():
    filename = sys.argv[1:2][0]
    #print(os.path.abspath(filename))
    #return
    if not os.path.exists(filename):
        print(f'{filename} does not exist')
        sys.exit(1)
    out_path = Path('web_' + filename).with_suffix('.mp4')
    os.system(f'ffmpeg -i "{filename}" -vf scale=640:-1 -c:v libx264 -crf 19 "{out_path}"')

if __name__ == "__main__":
    main()
