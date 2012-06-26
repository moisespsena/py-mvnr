# PyMVNR (Python MVN Recursively) 

Execute Apache Maven commands on projects recursively in dependency order.

## Dependencies

1.	Python Simple Directed Acyclic Graph: [py-sdag](https://github.com/moisespsena/py-sdag "Goto Python Simple Directed Acyclic Graph")
-	[Apache Maven](http://maven.apache.org "Goto Apache Maven home page")

## Install

1.	Install py-dag if not has be installed;
-	Install and configure Apache Maven;
-	Define the `M2_HOME` and `JAVA_HOME` enviroment variables if not be defined;
-	Clone this repo in your enviroment, execute `cd py-mvnr.git` and `python setup.py install`.

## Test

### Structure of the root directory of projects
	tests_resources/projects_root
		proj-a/
			pom.xml
		proj-b/
			pom.xml {
				dependencies:
					groupId:proj-c-sub-b:$project.version
			}
		proj-c/
			pom.xml
			proj-c-sub-a/
				pom.xml {
					dependencies:
						groupId:proj-c-sub-b:$project.version
						groupId:proj-a:1.0-SNAPSHOT
				}
			proj-c-sub-b
				pom.xml {
					dependencies:
						groupId:proj-a:1.0-SNAPSHOT
				}
			
### The build order

1.	groupId:proj-a:version
-	groupId:proj-c-b:version
-	groupId:proj-c-a:version	
-	groupId:proj-b:version

### Run Test

	cd tests_resources
	mvnr clean install
