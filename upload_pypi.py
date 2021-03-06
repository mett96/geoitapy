#!/usr/bin/env python

import os
from configparser import ConfigParser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--production', action="store_true", default=False,
                    help='Publish a production version of the package on pypi, otherwise public a '
                         'version on test pypi [default: False]')
args = parser.parse_args()

config: ConfigParser = ConfigParser()
config_path = '.geoitapy.conf'

if os.path.exists(config_path):
    config.read(config_path)
else:
    config['pypi'] = {
        "version": "0.0.1",
        "upload": 'no'
    }
    config['testpypi'] = {
        "version": "0.0.1",
        "upload": 'no'
    }
    config.write(open(config_path, 'w'))


if args.production:
    print('PRODUCTION')
    old_version = config.get('pypi', 'version')
else:
    print('TEST')
    old_version = config.get('testpypi', 'version')

print('Old version:', old_version)
new_version = input('New version: ')

els = new_version.split('.')
print(len(els))
if len(els) == 1:
    els += ['0', '0']
elif len(els) == 2:
    els.append('0')
elif len(els) == 3:
    pass
else:
    raise ValueError("The version has to be formatted X.Y.Z")

maj, mid, mino = els
maj, mid, mino = int(maj), int(mid), int(mino)
o_maj, o_mid, o_min = old_version.split('.')
o_maj, o_mid, o_min = int(o_maj), int(o_mid), int(o_min)

ok = False
if maj > o_maj:
    ok = True
elif mid > o_mid:
    ok = True
elif mino > o_min:
    ok = True

if not ok:
    raise ValueError(f"The new version has to be major then older ({new_version} < {old_version})")

print("New version:", maj, mid, mino)
new_version = '.'.join(els)

if args.production:
    config.set('pypi', 'version', new_version)
    config.set('pypi', 'upload', 'yes')
    config.set('testpypi', 'upload', 'no')
else:
    config.set('testpypi', 'version', new_version)
    config.set('testpypi', 'upload', 'yes')
    config.set('pypi', 'upload', 'no')

config.write(open(config_path, 'w'))

os.system("rm $WORKSPACE/Python/geoitapy/dist/*")
os.system("python setup.py sdist bdist_wheel")

if args.production:
    os.system("python -m twine upload dist/*")
else:
    os.system("python -m twine upload --repository testpypi dist/*")







