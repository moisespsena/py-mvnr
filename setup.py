#!/usr/bin/env python
from distutils.cmd import Command
from setuptools import setup
import os
import re
import sys
import shutil
import time
from subprocess import Popen

THIS_PATH = os.path.realpath(os.path.dirname(__file__))
PKG_DIR = os.path.join(THIS_PATH, "mvnr")
SCRIPTS_DIR = os.path.join(THIS_PATH, "scripts")

def read(fname):
    return open(os.path.join(THIS_PATH, fname)).read()
        
class TestCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        proc = Popen("cd '%s' && python '%s'" % (THIS_PATH, "tests.py",), shell=True, env=os.environ, stdout=sys.stdout, stderr=sys.stderr)
        proc.wait()
          
class CleanCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self.rmPaths = [ ]
        
        for f in os.listdir(THIS_PATH):
            if re.search("(^(build|dist)$|\.egg-info)", f):
                self.rmPaths.append(f)
                pass
            
        for root, dirs, files in os.walk(THIS_PATH):
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyo"):
                    self.rmPaths.append(os.path.join(root, f))

    def finalize_options(self):
        pass
                
    def run(self):
        for p in self.rmPaths:
            if os.path.isdir(p):
                print("Remove directory: " + p)
                shutil.rmtree(p, True)
            else:
                print("Remove file     : " + p)
                os.unlink(p)

setup(
    name="py-mvnr",
    version="1.0",
    author="Moises P. Sena",
    author_email="moisespsena@gmail.com",
    description=("PyMVNR (Python MVN Recursively) Execute Apache Maven commands on projects recursively."),
    long_description=read('README.md'),
    license="BSD",
    keywords="utils utilities maven mvn java apache recursive",
    url="https://github.com/moisespsena/py-mvnr",
    package_dir=dict(mvnr=PKG_DIR),
    packages=["mvnr"],
    scripts=[os.path.join(SCRIPTS_DIR, 'mvnr')],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: Build Tool",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7" 
    ],
    cmdclass={'test' : TestCommand, 'clean': CleanCommand}
)
