#!/usr/bin/env python3

import os
import string
import shutil
import toml
import argparse
import datetime
import subprocess

def update_AVAILABLE(input_dir, AVAILABLE_file):
    """
    """

    fnames = os.listdir(input_dir)
    fnames.sort()
    with open(AVAILABLE_file, 'w') as f:
        f.write('DATE     TIME      FILENAME    REFERENCE   ' + '\n')
        f.write('YYYYMMDD HHMMSS                GFYYYYmmddHH' + '\n')
        f.write('________ ______    ________    ____________' + '\n')
        for fname in fnames:
            date = fname[0:8]
            time = fname[8:10]+'0000'
            f.write(date + ' ' + time + '    ' + 'GF'+fname + '  ' + 'ON DISC' + '\n')

    print("AVAILABLE updated!")

def update_pathnames(source_dir, control_dir, output_dir, input_dir, AVAILABLE_file):
    with open(source_dir+'pathnames_template') as t_file:
        temp = t_file.read()
        temp = temp.split('====')[0]

    t = string.Template(temp)
    pathnames = t.substitute(control_dir=control_dir,
                             output_dir=output_dir,
                             input_dir=input_dir,
                             available_file=AVAILABLE_file)
    
    with open('pathnames', 'w') as file:
        file.write(pathnames)

    print("pathnames updated!")

def update_COMMAND(source_dir, control_dir, direction, begin_dt, end_dt, out_interval):
    with open(source_dir+'COMMAND_template') as t_file:
        temp = t_file.read()

    begin = datetime.datetime.strptime(begin_dt, "%Y%m%d")
    end = datetime.datetime.strptime(end_dt, "%Y%m%d")

    t = string.Template(temp)
    COMMAND = t.substitute(direction=direction,
                           begin_date=begin.strftime("%Y%m%d"),
                           begin_time=begin.strftime("%H%M%S"),
                           end_date=end.strftime("%Y%m%d"),
                           end_time=end.strftime("%H%M%S"),
                           out_interval='{:.0f}'.format(out_interval))

    with open(control_dir+'COMMAND', 'w') as file:
        file.write(COMMAND)

    print("COMMAND updated!")

def update_RELEASES(source_dir, control_dir, species, heights, no_part, time, bboxes):
    with open(source_dir+'RELEASES_header_template') as t_file:
        header_temp = t_file.read()

    header_t = string.Template(header_temp)
    RELEASES = header_t.substitute(species=species)

    with open(source_dir+'RELEASES_template') as t_file:
        temp = t_file.read()
    
    t = string.Template(temp)
    for bbox in bboxes:
        for h in heights:
            c = str((h[0]+h[1])/2.) + 'm ' + str(no_part)
            RELEASES += t.substitute(begin=time[0].strftime("%Y%m%d %H%M%S"),
                                     end=time[1].strftime("%Y%m%d %H%M%S"),
                                     lon_ll='%9.4f' % bbox['lon_ll'],
                                     lat_ll='%9.4f' % bbox['lat_ll'],
                                     lon_ur='%9.4f' % bbox['lon_ur'],
                                     lat_ur='%9.4f' % bbox['lat_ur'],
                                     lower='%9.3f' % h[0],
                                     upper='%9.3f' % h[1],
                                     no_part='%9d' % no_part,
                                     comment=c)

    with open(control_dir+'RELEASES', 'w') as file:
        file.write(RELEASES)

    print("RELEASES updated!")

parser = argparse.ArgumentParser(usage="usage")
parser.add_argument("--direction", help='forward or backward')
parser.add_argument("--input", default='gfs_083.2', help='ECMWF, gfs_083.2, gfs_083.3')
#TODO: input names
parser.add_argument("--station", help='Back-trajectory release station name')
parser.add_argument("--date", help='Back-trajectory reach date YYYYmmdd')
args = parser.parse_args()

print('args', args)

if args.input not in ['ECMWF', 'gfs_083.2', 'gfs_083.3']:
    raise ValueError

control_dir = './options/'
AVAILABLE_file = './AVAILABLE'
mount_dir = '/home/muditha/0_Research/FLEXPART/flexpart_10-4_docker/'
input_dir = mount_dir+'data/'+args.input+'/'
source_dir = mount_dir+'source_files/'

config_file = toml.load(source_dir+'config_{}.toml'.format(args.station))

dt = args.date
output_dir = mount_dir+'output_files/{}/{}_{}/'.format(args.station, datetime.datetime.strptime(dt, "%Y%m%d").strftime("%Y%m%d_%H"), args.direction)
print('output_dir: ', output_dir)

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)
else:
    os.makedirs(output_dir)

update_AVAILABLE(input_dir, AVAILABLE_file)
update_pathnames(source_dir, control_dir, output_dir, input_dir, AVAILABLE_file)
if args.direction=='forward':
    direction = 1
    update_COMMAND(source_dir, control_dir, direction,
                   begin_dt=dt,
                   end_dt=(datetime.datetime.strptime(dt, "%Y%m%d")+datetime.timedelta(hours=config_file['time']['tr_duration'])).strftime("%Y%m%d"), 
                   out_interval=config_file['time']['outstep'])
elif args.direction=='backward':
    direction= -1
    update_COMMAND(source_dir, control_dir, direction,
                   begin_dt=(datetime.datetime.strptime(dt, "%Y%m%d")-datetime.timedelta(hours=config_file['time']['tr_duration'])).strftime("%Y%m%d"), 
                   end_dt=dt,
                   out_interval=config_file['time']['outstep'])
else:
    raise ValueError

no_of_releases = len(config_file['station']['lon'])
bboxes = []
for release in range(no_of_releases):
    bboxes = bboxes + [{'lon_ll': config_file['station']['lon'][release]-0.1, 'lat_ll': config_file['station']['lat'][release]-0.1, 
                        'lon_ur': config_file['station']['lon'][release]+0.1, 'lat_ur': config_file['station']['lat'][release]+0.1}]
#bboxes = [{'lon_ll': config_file['station']['lon'][0]-0.1, 'lat_ll': config_file['station']['lat'][0]-0.1,
#           'lon_ur': config_file['station']['lon'][0]+0.1, 'lat_ur': config_file['station']['lat'][0]+0.1},
#          {'lon_ll': config_file['station']['lon'][1]-0.1, 'lat_ll': config_file['station']['lat'][1]-0.1,
#           'lon_ur': config_file['station']['lon'][1]+0.1, 'lat_ur': config_file['station']['lat'][1]+0.1}]
center_heights = list(range(config_file['height']['base'], 
                            config_file['height']['top']+1, 
                            config_file['height']['interval']))
plusminus_height = config_file['release']['rel_pm_height']
heights = [(h-plusminus_height, h+plusminus_height) for h in center_heights]
if args.direction=='forward':
    time = [datetime.datetime.strptime(dt, "%Y%m%d"),
            datetime.datetime.strptime(dt, "%Y%m%d")+datetime.timedelta(minutes=config_file['release']['rel_after_minutes'])]
elif args.direction=='backward':
    time = [datetime.datetime.strptime(dt, "%Y%m%d")-datetime.timedelta(minutes=config_file['release']['rel_after_minutes']),
            datetime.datetime.strptime(dt, "%Y%m%d")]

update_RELEASES(source_dir, control_dir, 
                species=config_file['release']['species_no'], 
                heights=heights, 
                no_part=config_file['release']['no_particles'], 
                time=time, bboxes=bboxes)

process = subprocess.run('./src/FLEXPART', shell=True, check=True,
                         stdout=subprocess.PIPE, universal_newlines=True)
print(process.stdout)

#Change output file permissions
for root, dirs, files in os.walk(output_dir):
    os.chmod(os.path.join(root), 0o777)
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o777)
    for f in files:
        os.chmod(os.path.join(root, f), 0o777)
