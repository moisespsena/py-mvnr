# -*- coding: utf-8 -*-
'''
Created on 07/12/2011

@author: Moises P. Sena "<moisespsena" + "@" + "gmail.com>"
'''

__author__ = "Moises P. Sena"
__version__ = "1.0"

from collections import OrderedDict
from mvnr.Project import Project
from sdag.DAG import DAG
from sdag.TopologicalSorter import sort as tsort
from xml.dom.minidom import parse
import logging
import os

logger = logging.getLogger("mvnr")
        
USER_M2_REPOSITORY = os.path.join(os.path.expanduser("~"), ".m2", "repository")

class DuplicateProjectDetected(Exception):
    def __init__(self, pomFiles, name):
        self.value = "The project '%s' has be duplicated: '%s'" % (name, "' and '".join(pomFiles))
        
    def __str__(self):
        return repr(self.value)
        
class ProjectsLoader:
    def __init__(self, pomFiles, repositoryPath=USER_M2_REPOSITORY, logEnable=True):
        self.pomFiles = pomFiles
        self.projects = {}
        self.dag = DAG()
        self.ordenedProjects = None
        self.logEnabled = logEnable
        self.repositoryPath = repositoryPath
        
    def xmlChildByTagName(self, el, name):
        for i in el.childNodes:
            if i.nodeType == i.ELEMENT_NODE and i.tagName == name:
                return i
            
        return None
    
    def nodeValue(self, el):
        if el != None:
            if el.nodeType == el.ELEMENT_NODE and el.firstChild != None and el.firstChild.nodeType == el.TEXT_NODE:
                return el.firstChild.data
        
        return None
    
    def doValue(self, node, tagName, inherits=True):
        value = self.nodeValue(self.xmlChildByTagName(node, tagName))
        
        if value == None and inherits:
            node = self.xmlChildByTagName(node, 'parent')
            
            if node != None:
                value = self.nodeValue(self.xmlChildByTagName(node, tagName))
                
        return value
    
    def rootOnProjectsOf(self, project):
        pomXml = project.get_element()
        parentNode = self.xmlChildByTagName(pomXml, 'parent')
        
        if parentNode:
            pArtifactId = self.doValue(parentNode, 'artifactId')
            pGroupId = self.doValue(parentNode, 'groupId')
            pVersion = self.doValue(parentNode, 'version')
            
            parent = Project(pGroupId, pArtifactId, pVersion)
            parentId = parent.pid()
            
            if parentId in self.projects:
                parentProject = self.projects[parentId]
                doParent = self.rootOnProjectsOf(parentProject)
                
                if doParent:
                    return doParent
                else:
                    return parentProject
        return None
    
    def parentOf(self, project):
        pomXml = project.get_element()
        parentNode = self.xmlChildByTagName(pomXml, 'parent')
        
        if parentNode:
            pArtifactId = self.doValue(parentNode, 'artifactId')
            pGroupId = self.doValue(parentNode, 'groupId')
            pVersion = self.doValue(parentNode, 'version')
            
            parent = Project(pGroupId, pArtifactId, pVersion)
            parentId = parent.pid()
            
            if parentId in self.projects:
                parentProject = self.projects[parentId]
                
                return parentProject
        return None
        
    def createProjectOfElement(self, element, this=None):        
        artifactId = self.doValue(element, 'artifactId')
        groupId = self.doValue(element, 'groupId')
        version = self.doValue(element, 'version')
        
        if artifactId and groupId and version:
            if this != None:
                if artifactId == "${project.artifactId}":
                    artifactId = this.get_artifactId()
                if groupId == "${project.groupId}":
                    groupId = this.get_groupId()
                if version == "${project.version}":
                    version = this.get_version()
            
            project = Project(groupId, artifactId, version, element)
            
            return project;
        
        return None
    
    def resolveDependencyInRepository(self, project):
        if project.parent != None:
            if project.parent.pid() in self.projects:
                # if parent project has be installed, does not 
                # run in this (mvn rum all sub modules)
                if not os.path.isfile(project.parent.repositoryPom):
                    return self.resolveDependencyInRepository(project.parent)
        
        return project
        
    def loadProjects(self):
        for pomFile in  self.pomFiles:
            element = parse(pomFile).documentElement
            project = self.createProjectOfElement(element)
            
            project.pomFile = pomFile
            project.projectPath = os.path.dirname(pomFile)
            
            repository = self.repositoryPath
            repository = os.path.join(repository, project.groupId.replace(".", os.path.sep), project.artifactId, project.version)
            repository = os.path.abspath(repository)
            
            project.repositoryPath = repository
            project.repositoryPom = os.path.join(repository, project.artifactId + "-" + project.version + ".pom")
            
            if project.pid() in self.projects:
                raise DuplicateProjectDetected([pomFile, self.projects[project.pid()].pomFile], project.pid())
            
            packaging = self.nodeValue(self.xmlChildByTagName(element, 'packaging'))
            
            if "pom" == packaging:
                project.set_isParent(True)
            
            self.projects[project.pid()] = project
                
        for pid in self.projects:
            project = self.projects[pid]
            element = project.get_element()
            dependencies = self.xmlChildByTagName(element, 'dependencies')
            project.parent = self.parentOf(project)
            
            if dependencies:
                for dependency in dependencies.childNodes:
                    if dependency.nodeType != dependency.ELEMENT_NODE:
                        continue
                    
                    dependencyProject = self.createProjectOfElement(dependency, project)
                    
                    if dependencyProject:
                        dependencyId = dependencyProject.pid()
                        
                        if dependencyId in self.projects:
                            dependencyProject = self.projects[dependencyId]
                            project.addDependency(dependencyProject)
                            
        if self.logEnabled:
            logger.info("The Dependence Tree is:")
            logger.info("")
        
        
        i = 0
        
        for pid in self.projects:
            i = i + 1
            
            if self.logEnabled:
                logger.info(("%4s" % "") + " " + str(i) + ". " + pid)
            
            pVertex = self.dag.addVertex(pid)
            
            for d in self.projects[pid].get_dependencies():
                if self.logEnabled:
                    logger.info(("%6s" % "") + ("%4s" % "") + "- " + d.pid())
                
                dVertex = self.dag.addVertex(d.pid())
                self.dag.addEdge(dVertex, pVertex)
        
        self.ordenedProjects = OrderedDict()
        
        reactorOrder = tsort(self.dag)
        
        if self.logEnabled:
            logger.info("")
            logger.info("The Reactor Order is:")
            logger.info("")
        
        i = 1
        
        for pid in reactorOrder:
            project = self.projects[pid]
            
            self.ordenedProjects[pid] = project
            
            if self.logEnabled:
                logger.info("%6s" % str(i) + ". " + pid)
                
            i = i + 1

        if self.logEnabled:
            logger.info("")
