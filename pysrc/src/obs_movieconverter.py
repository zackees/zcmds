""" Converts obs movies to a format usable by imovie """

import os
import sys
from shutil import copyfile

files = sorted([f for f in os.listdir(".") if ".mp4" in f and "2020" in f])
out_files = ["new_" + f + ".mov" for f in files]
rtn_codes = []

for count, f in enumerate(files):
    input = f
    out = out_files[count]
    cmd = (
        "ffmpeg -i "
        + input
        + " -c:a aac -c:v libx264 -crf 20 -preset fast -f mov "
        + out
    )
    # cmd = 'handbrakecli -i ' + input + ' -o ' + out + ' -e x264 -q 20 -B 160 --aencoder mp3'
    print(cmd)
    rtn = os.system(cmd)
    rtn = 0
    rtn_codes.append(rtn)

any_failed = False

for count, rtn in enumerate(rtn_codes):
    if rtn != 0:
        print("Exited because of error code " + str(rtn) + " in file " + files[count])

if any_failed:
    print("One or more files failed, aborting file replacement")
    sys.exit(0)

for count, f in enumerate(files):
    copyfile(out_files[count], f)


# os.system('handbrakecli -i 2020-11-24_18-12-06.mp4 -o movie.mp4 -e x264 -q 20 -B 160')
