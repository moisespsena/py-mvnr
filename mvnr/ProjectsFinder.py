# -*- coding: utf-8 -*-
'''
Created on 07/12/2011

@author: Moises P. Sena "<moisespsena" + "@" + "gmail.com>"
'''

__author__ = "Moises P. Sena"
__version__ = "1.0"

import os
import re

class ProjectsFinder(object):
    FILE_NAME = 'pom.xml'

    def __init__(self, ignore, path):
        '''
        Constructor
        '''
        self.ignore = ignore
        self.path = path
        
    def doFind(self, path, result):
        for fileName in os.listdir(path):
            if re.search(self.ignore, fileName):
                continue
            
            filePath = os.path.join(path, fileName)
            
            if os.path.isdir(filePath):
                self.doFind(filePath, result)
            elif ProjectsFinder.FILE_NAME == fileName:
                result.append(filePath)
     
    def find(self):
        result = []
        self.doFind(self.path, result)
        
        return result
        
