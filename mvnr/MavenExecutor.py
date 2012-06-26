# -*- coding: utf-8 -*-
'''
Created on 15/12/2011

@author: Moises P. Sena "<moisespsena" + "@" + "gmail.com>"
'''

__author__ = "Moises P. Sena"
__version__ = "1.0"

import logging
import os
from subprocess import Popen, CalledProcessError
import pipes

logger = logging.getLogger("mvnr")

M2_HOME = "M2_HOME"
JAVA_HOME = "JAVA_HOME"
PATH = "PATH"

class EnvVariableNotSet(Exception):
    def __init__(self, varName):
        self.value = varName + " environment variable was not set." 
                 
    def __str__(self):
        return repr(self.value)
    
class MavenExecutor(object):
    '''
    Executa o maven em um projeto
    '''


    def __init__(self, ordenedProjects, stdout=None, stderr=None):
        '''
        Constructor
        '''
        self.ordenedProjects = ordenedProjects
        self.removeRepository = False
        self.env = os.environ.copy()
        self.stdout = stdout
        self.stderr = stderr
        
    def rum(self, popenargs):
        popenargs = popenargs if isinstance(popenargs, basestring) else ("'" + "' '".join([unicode(a.replace("\\", "\\\\").replace("'", "\\'")) for a in popenargs]) + "'")
        return self.check_output(popenargs, shell=True, env=self.env, stdout=self.stdout, stderr=self.stderr)
        
    def check_output(self, *popenargs, **kwargs):
        popenargs =[unicode(a) for a in popenargs]
        process = Popen(popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output
        
    def execute(self, commandArgs):
        if not M2_HOME in self.env:
            raise EnvVariableNotSet(M2_HOME)
        
        if not JAVA_HOME in self.env:
            raise EnvVariableNotSet(JAVA_HOME)
        
        if not PATH in self.env:
            self.env[PATH] = ""
            
        self.env[PATH] = self.env[PATH] + os.pathsep + os.path.join(self.env[M2_HOME], "bin")
        
        NON_RECURSIVE_OPTION = "--non-recursive"
        NON_RECURSIVE_SHORT_OPTION = "-N"
        
        hasNonRecursive = False
        
        for v in commandArgs:
            if v == NON_RECURSIVE_OPTION or v == NON_RECURSIVE_SHORT_OPTION:
                hasNonRecursive = True
                
        if not hasNonRecursive:
            commandArgs.append(NON_RECURSIVE_OPTION)
        
        for i in range(len(commandArgs)):
            commandArgs[i] = pipes.quote(commandArgs[i])
            
        command = " ".join(commandArgs)
        
        logger.info("Execute %s in projects", command)
        logger.info("")
        
        size = len(self.ordenedProjects)
        cur = 0
        
        for pid in self.ordenedProjects:
            cur = cur + 1
            project = self.ordenedProjects[pid]
            
            logger.info("(%s/%s) %s: Processing...", cur, size, pid)
            
            allowRemoveRepository = len([item for item in ['install', 'deploy'] if item in commandArgs]) > 0
            
            if allowRemoveRepository and self.removeRepository:
                rm = ['rm', '-rf', project.repositoryPath]
                logger.info("Execute: %4s", " ".join(rm))
                self.rum(rm)
            
            rum = "cd '%s' && %s" % (project.projectPath, command)
            
            logger.info("(%s/%s) %s: Execute: ", cur, size, pid)
            logger.info("%4s$ %s", "", rum)
            
            self.rum(rum)  
