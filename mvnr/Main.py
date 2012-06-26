# -*- coding: utf-8 -*-
'''
Created on 01/03/2012

@author: moi
'''

__author__ = "Moises P. Sena"
__version__ = "1.0"

from optparse import OptionParser, OptionGroup
from mvnr.Formatter import Formatter
from mvnr.MavenExecutor import MavenExecutor, EnvVariableNotSet
from mvnr.ProjectsFinder import ProjectsFinder
from mvnr.ProjectsLoader import ProjectsLoader, DuplicateProjectDetected, \
    USER_M2_REPOSITORY
from subprocess import CalledProcessError
import logging
import os
import sys

DEFAULT_IGNORE = "^\\.|target"

def _command(command):
    if len(command) > 0 and command[0] == sys.argv[0]:
        command = command[1:]
    
    if len(command) == 0:
        return None
    
    if command[0].strip() != "mvn":
        command.insert(0, "mvn")
        
    return command

def main(args=[]):
    parser = OptionParser(
        usage="usage: %prog [options] mvnArg1 [mvnArg ...]",
        version="1.0",
        formatter=Formatter())
    parser.add_option("--d",
                      default=os.getcwd(),
                      dest="PROJECTS_DIRECTORY",
                      help="The projects diretory to rum command. Default is CWD.")
    parser.add_option("--i",
                      dest="IGNORE_FILES",
                      help="Files do ignore on find projects using regex. Use pipe to separate expressions. "
                      "Ex.: '\\.git|\\.svn|\\.project|target'. Default is: " + DEFAULT_IGNORE,
                      default=DEFAULT_IGNORE,
                      type="string")
    parser.add_option("--r",
                      default=USER_M2_REPOSITORY,
                      dest="REPOSITORY",
                      help="The Maven Local Repository Path. Default is '" + USER_M2_REPOSITORY + "'")
    parser.add_option("--c",
                      default=False,
                      action="store_true",
                      dest="NO_REMOVE_CACHE",
                      help="Remove Maven Local Repository Cache in REPOSITORY/<groupId>/" + \
                        "<artifactId>/<version> of each proccessed project.")
    parser.add_option("--l",
                      default=False,
                      action="store_true",
                      dest="LIST",
                      help="List all projects.")
    parser.add_option("--s",
                      default=False,
                      action="store_true",
                      dest="SHOW",
                      help="Shown options values.")
    
    group = OptionGroup(parser, "Examples",
                    '''
    %prog clean package''')
    parser.add_option_group(group)
    
    group = OptionGroup(parser, "Exit Status",
'''
    0 - Successful
    1 - JAVA_HOME or M2_HOME enviroment variables does not be setted
    2 - Program options/arguments error"
    6 - The Apache Maven Error
''')
    parser.add_option_group(group)
    
    (options, args) = parser.parse_args(args)
    
    command = args
    
    options.PROJECTS_DIRECTORY = os.path.abspath(os.path.realpath(os.path.expanduser(options.PROJECTS_DIRECTORY)))
    
    command = _command(command)
    
    if options.SHOW:
        dc = dict(PROJECTS_DIRECTORY=options.PROJECTS_DIRECTORY, 
                  IGNORE_FILES=options.IGNORE_FILES, 
                  REPOSITORY=options.REPOSITORY, 
                  NO_REMOVE_CACHE=options.NO_REMOVE_CACHE, 
                  LIST=options.LIST, 
                  SHOW=options.SHOW, MAVEN_COMMAND=("'" + "' '".join([c.replace("\\", "\\\\").replace("'", "\\'") for c in command]) + "'" if command else ""))
        for k,v in dc.items():
            print("%s = %s" %(k, v))
        
        return
    
    projectsDirectory = options.PROJECTS_DIRECTORY
        
    logging.basicConfig(format="[%(levelname)s] [%(name)s] [%(asctime)s]: %(message)s", level=logging.INFO, stream=sys.stdout)
    
    logger = logging.getLogger("mvnr")
    
    finder = ProjectsFinder(options.IGNORE_FILES, projectsDirectory)
    
    projects = finder.find()
    
    if len(projects) == 0:
        logger.info("No Projects Found")
    else :
        loader = ProjectsLoader(projects, options.REPOSITORY)
    
        try:
            loader.loadProjects()
            
            if not options.LIST:
                executor = MavenExecutor(loader.ordenedProjects)
                executor.removeRepository = not options.NO_REMOVE_CACHE
    
                if command is None:
                    parser.error("No maven commands found.")
                    return;
                    
                executor.execute(command)
        
        except EnvVariableNotSet as e:
            logger.error(e)
            sys.exit(1)
        except DuplicateProjectDetected as e:
            logger.error(e)
            sys.exit(4)
        except CalledProcessError as e:
            logger.error(e)
            sys.exit(6)
        except KeyboardInterrupt as e:
            logger.info("done.")
            print("")

if __name__ == '__main__':
    main(sys.argv)
