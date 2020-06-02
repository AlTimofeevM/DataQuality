from __future__ import print_function

import os
import subprocess

from setuptools import setup, find_packages


data_files = []

conf_dir = "/etc/sawtooth"

if os.path.exists("/etc/default"):
    data_files.append(
        ('/etc/default', ['packaging/systemd/dataquality-tp-python']))

if os.path.exists("/lib/systemd/system"):
    data_files.append(
        ('/lib/systemd/system',
         ['packaging/systemd/dataquality-tp-python.service']))

setup(
    name='dq',
    version=subprocess.check_output(
        ['../../bin/get_version']).decode('utf-8').strip(),
    description='Data Quality Controller Example',
    author='Timofeev Alexander',
    url='https://github.com/AlTimofeevM/DataQuality',
    packages=find_packages(),
    install_requires=[
        "cbor",
        "colorlog",
        "sawtooth-sdk",
        "sawtooth-signing",
        "request",
        "secp256k1"
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'dq = dataquality.client_cli.dq_cli:main_wrapper',
            'dataquality-tp-python = dataquality.processor.main:main'
        ]
    })
