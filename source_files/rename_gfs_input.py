#!/usr/bin/env python3

import os

input_dir = '/home/muditha/0_Research/FLEXPART/flexpart_10-4_docker/data/gfs_083.2/'

fnames = os.listdir(input_dir)

for fname in fnames:
    os.rename(input_dir+fname, input_dir+'20'+fname)
