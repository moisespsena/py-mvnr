# -*- coding: utf-8 -*-
'''
Created on 07/12/2011

@author: Moises P. Sena "<moisespsena" + "@" + "gmail.com>"
'''
__author__ = "Moises P. Sena"
__version__ = "1.0"

class Project(object):
    '''
    classdocs
    '''
    
    def __init__(self, groupId, artifactId, version, element = None, projectPath = None):
        '''
        Constructor
        '''
        self.artifactId = artifactId
        self.groupId = groupId
        self.version = version
        self.element = element
        self.dependencies = {}
        self.modules = None
        self.isParent = False
        self.parent = None
        self.dependency = self
        self.proccess = True
        self.projectPath = projectPath
        self.repositoryPath = None
        self.pomFile = None
        
    def get_element(self):
        return self.element
        
    def set_dependencies(self, value):
        self.dependencies = value
        
    def set_modules(self, value):
        self.modules = value
        
    def set_isParent(self, value):
        self.isParent = value
        
    def set_parent(self, value):
        self.parent = value
        
    def get_artifactId(self):
        return self.artifactId
        
    def get_groupId(self):
        return self.groupId
        
    def get_version(self):
        return self.version
        
    def get_dependencies(self):
        return self.dependencies
        
    def get_modules(self):
        return self.modules
        
    def get_isParent(self):
        return self.isParent
        
    def get_parent(self):
        return self.parent
        
    def pid(self):
        return self.groupId + ":" + self.artifactId + ":" + self.version
    
    def addDependency(self, value):
        self.dependencies[value] = value
        
    def rmDependency(self, value):
        del self.dependencies[value]
        
    def getProjectPath(self):
        return self.projectPath
    
    def __hash__(self):
        return self.pid().__hash__()
    
    def __str__(self):
        return "Project{" + self.pid() + "}"
    
    def __eq__(self, other):
        if isinstance(other, Project):
            if(self.id() == other.pid()):
                return True;
        return False
    
    def __nq__(self, other):
        return not self.__eq__(other)