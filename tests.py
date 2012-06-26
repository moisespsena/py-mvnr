#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 02/03/2012

@author: moi
'''

import logging
import os
import sys
import unittest
import subprocess
import shutil

from mvnr.MavenExecutor import MavenExecutor
from mvnr.ProjectsFinder import ProjectsFinder
from mvnr.ProjectsLoader import ProjectsLoader
    
class NullDevice:
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        pass
    def __getattr__(self, attr):
        return getattr(self.stream, attr)
    

resourcesPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tests_resources")
projectsRoot = os.path.join(resourcesPath, "projects-root")
repositoryPath = os.path.join(resourcesPath, "repository")
    
def _configureLogger():
    logging.basicConfig(format="[%(levelname)s] [%(asctime)s] [%(name)s]: %(message)s", level=logging.INFO, stream=sys.stdout)
    
class Test(unittest.TestCase):
    def testDependencyOrder(self):
        _configureLogger()
        finder = ProjectsFinder("^\\.", projectsRoot)
        pomFiles = finder.find()
        
        repositoryPath = os.path.join(resourcesPath, "repository")
        
        loader = ProjectsLoader(pomFiles, repositoryPath)
        loader.loadProjects()
        
        o = []
        
        for p in loader.ordenedProjects:
            o.append(p)
        
        p1 = o.index("sample-group:project-1:1.0-SNAPSHOT")
        self.assertTrue(p1 > -1)
        p2 = o.index("sample-group:project-2:1.0-SNAPSHOT")
        self.assertTrue(p2 > -1)
        p3 = o.index("sample-group:project-3:1.0-SNAPSHOT")
        self.assertTrue(p3 > -1)
        p3a = o.index("sample-group:project-3-sub-a:1.0-SNAPSHOT")
        self.assertTrue(p3a > -1)
        p3b = o.index("sample-group:project-3-sub-b:1.0-SNAPSHOT")
        self.assertTrue(p3b > -1)
        
        self.assertTrue(p2 > p3b)
        self.assertTrue(p3a > p3b)
        self.assertTrue(p3a > p2)
        
            
    def testExecuteInstall(self):
        _configureLogger()
        
        finder = ProjectsFinder("^\\.", projectsRoot)
        pomFiles = finder.find()
        
        if os.path.exists(repositoryPath):
            shutil.rmtree(repositoryPath)
            
        os.mkdir(repositoryPath)
        
        loader = ProjectsLoader(pomFiles, repositoryPath)
        loader.loadProjects()
        
        executor = MavenExecutor(loader.ordenedProjects, subprocess.PIPE)
        executor.removeRepository = False
        try:
            executor.execute(['mvn', "-Dmaven.repo.local=%s" % (repositoryPath,), 'clean', 'install'])
        finally:
            shutil.rmtree(repositoryPath)

if __name__ == "__main__":
    unittest.main()
