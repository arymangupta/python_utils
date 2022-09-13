import sys
import platform
import shutil
import os
import logging

# # Construct the argument parser
# ap = argparse.ArgumentParser()
#
# # Add the arguments to the parser
# ap.add_argument("--serverType", type=str, required=True, help="Any one of Tomcat, Jboss, Weblogic, WebSphere, "
#                                                               "Wildfly, Jetty, ExecutableJar")
# ap.add_argument("--startUpScriptPath", type=str, required=True, help="Config File that is used for adding javaagent")
# ap.add_argument("--appContext", type=str, required=True, help="App Context specific to each application")
# ap.add_argument("--applicationType", type=str, help="Application Type like Liferay, Jira, webgoat")
# ap.add_argument("--filterType", type=str, help="ServletFilter or PortletFilter")
# ap.add_argument("--instrumentationFilterClass", type=str, help="Name of the filter to be instrumented")
# ap.add_argument("--filterMethod", type=str, help="API in the filter to be instrumented")
# ap.add_argument("--filterPosition", type=str, help="First or Last. Only Last has significance")
# args = vars(ap.parse_args())
#
# print("args passed : " + str(args))
#
# if len(args['serverType']) <= 0:
#     raise ValueError('Please provide server type')
# if len(args['appContext']) <= 0:
#     raise ValueError('Please provide app context')
# if len(args['startUpScriptPath']) <= 0:
#     raise ValueError('Please provide startUpScriptPath')
# if not os.path.isfile(args['startUpScriptPath']):
#     if not ((str(args['startUpScriptPath']).endswith('setenv.sh') or str(args['startUpScriptPath']).endswith('setEnv.bat')) and str(args['serverType']) == 'Tomcat'):
#         raise ValueError('Please provide valid start up file where JVM args can be added')

def validate_args(server, startup_script_path, app_context):
    if len(server) <= 0 or len(startup_script_path) <= 0 or len(app_context) <= 0:
        logging.warning('Arguments are invalid')
        return False
    return True


def provision_java(server, startup_script_path, app_context, app_type, filter_type, inst_position, inst_class, inst_filter_method):
    logging.debug('Passed args : server=' + str(server) + ' startup_script_path=' + startup_script_path + ' app_context=' + app_context)
    if not validate_args(server, startup_script_path, app_context):
        return False

    if not os.path.isfile(startup_script_path):
        if not ((str(startup_script_path).endswith('setenv.sh') or str(startup_script_path).endswith('setEnv.bat')) and str(server) == 'Tomcat'):
            logging.warning("Wrong startup script path given or file not present")
            logging.warning("Please provide valid start up file where JVM args can be added")
            return False


    isLinux = True
    VSP_HOME = '/opt/virsec'
    if platform.system() == "Windows" or platform.system() == "windows":
        isLinux = False
        VSP_HOME = os.getenv('VSP_HOME')
        if VSP_HOME is None:
            VSP_HOME = "C:\\Program Files (x86)\\Virsec"

    # change iae.properties file with instrumentation details
    if isLinux:
        iae_context_file = VSP_HOME + '/iae-java/iae-' + app_context + '.properties'
        log_config_file = VSP_HOME + '/iae-java/logging-' + app_context + '.properties'
        if not os.path.isfile(iae_context_file):
            iae_file = shutil.copy(VSP_HOME + '/iae-java/iae.properties', iae_context_file)
            logging.debug('Created iae file linux : ' + str(iae_file))
        else:
            logging.debug('iae file already present')
        if not os.path.isfile(log_config_file):
            iae_file = shutil.copy(VSP_HOME + '/iae-java/logging.properties', log_config_file)
            logging.debug('Created log config file linux : ' + str(iae_file))
        else:
            logging.debug('log config file already present')
    else:
        iae_context_file = VSP_HOME + '\\iae-java\\iae-' + app_context + '.properties'
        log_config_file = VSP_HOME + '\\iae-java\\logging-' + app_context + '.properties'
        if not os.path.isfile(iae_context_file):
            iae_file = shutil.copy(VSP_HOME + '\\iae-java\\iae.properties', iae_context_file)
            logging.debug('Created iae file windows: ' + str(iae_file))
        else:
            logging.debug('iae file already present')
        if not os.path.isfile(log_config_file):
            iae_file = shutil.copy(VSP_HOME + '\\iae-java\\logging.properties', log_config_file)
            logging.debug('Created log config file windows: ' + str(iae_file))
        else:
            logging.debug('log config file already present')

    if not os.path.isfile(startup_script_path):
        # dummy file for tomcat setenv.sh
        with open(str(startup_script_path), 'w') as f:
            f.write("\n")
            f.close()

    if not os.path.isfile(startup_script_path + '.unprov'):
        shutil.copy(startup_script_path, startup_script_path+'.unprov')
        logging.debug("Taken backup of script file")
    else:
        if str(server).upper() == 'EXECUTABLEJAR':
            with open(startup_script_path, 'r') as f:
                data = f.read()
                if data.find('instrumentation.jar') != -1:
                    logging.info("java agent already added")
                    sys.exit(0)
        shutil.copy(startup_script_path + '.unprov', startup_script_path)

    if str(server).upper() in ['TOMCAT', 'JBOSS', 'WILDFLY', 'WEBLOGIC', 'JETTY', 'EXECUTABLEJAR', 'GLASSFISH']:
        f = open(startup_script_path, 'r')
        temp = f.read()
        f.close()

        f = open(startup_script_path, 'r')
        first_line = f.readline()
        f.close()

        f = open(startup_script_path, 'w')
        if isLinux:
            if first_line.startswith('#!'):
                f.write(first_line + "\n")
            f.write("export JAVA_TOOL_OPTIONS=\"$JAVA_TOOL_OPTIONS -javaagent:" + VSP_HOME + "/iae-java/instrumentation.jar "
                    "-Dvirsec_appcontextpath=" + app_context + " -DVSP_HOME=" + VSP_HOME + "\"\n\n")
        else:
            f.write("@echo off\n\nECHO.%JAVA_TOOL_OPTIONS%| FIND /I \"instrumentation.jar\">Nul || (\n"
                    "   set JAVA_TOOL_OPTIONS=%JAVA_TOOL_OPTIONS% -javaagent:\"%VSP_HOME%\"\\iae-java\\instrumentation.jar "
                    "-Dvirsec_appcontextpath=" + app_context + "\n)\n\n")

        if str(server).upper() == 'EXECUTABLEJAR':
            temp = temp.replace("-version 2>&1 |", "-version 2>&1 | grep -v \"instrumentation.jar\" |")

        f.write(temp)
        f.close()
    elif str(server).upper() == 'WEBSPHERE':
        f = open(startup_script_path, 'r')
        temp = f.read()
        f.close()

        f = open(startup_script_path, 'w')
        if isLinux:
            temp = temp.replace("genericJvmArguments=\"", "genericJvmArguments=\"-javaagent:" + VSP_HOME +
                                "/iae-java/instrumentation.jar -Dvirsec_appcontextpath=" + app_context +
                                " -DVSP_HOME=" + VSP_HOME + " ")
        else:
            VSP_HOME = VSP_HOME.replace("Program Files (x86)", "PROGRA~2")
            VSP_HOME = VSP_HOME.replace("Program Files", "PROGRA~1")
            temp = temp.replace("genericJvmArguments=\"", "genericJvmArguments=\"-javaagent:" + VSP_HOME +
                                "\\iae-java\\instrumentation.jar -Dvirsec_appcontextpath=" + app_context +
                                " ")
        f.write(temp)
        f.close()

    logging.debug('Edited the startup file successfully')
    return True

# # Construct the argument parser
# ap = argparse.ArgumentParser()
#
# # Add the arguments to the parser
# ap.add_argument("--serverType", type=str, required=True, help="Any one of Tomcat, Jboss, Weblogic, WebSphere, "
#                                                               "Wildfly, Jetty, ExecutableJar")
# ap.add_argument("--startUpScriptPath", type=str, required=True, help="Config File that is used for adding javaagent")
# ap.add_argument("--appContext", type=str, required=True, help="App Context specific to each application")
# args = vars(ap.parse_args())
#
# print("args passed : " + str(args))

def unprovision_java(server, startup_script_path, app_context):
    logging.debug('Passed args : server=' + str(server) + ' startup_script_path=' + startup_script_path + ' app_context=' + app_context)
    if not validate_args(server, startup_script_path, app_context):
        return False

    if os.path.isfile(startup_script_path + '.unprov'):
        shutil.copy(startup_script_path + '.unprov', startup_script_path)
        logging.debug("Copied back original file")
    else:
        logging.debug("unprov file not present")
    return True


def provJava(action, serverType, 
    appConfigFilePath, 
    appContextPath, 
    serverName, 
    applicationType, 
    filterType,
    instrumentationFilterClass,
    filterMethod,
    filterPosition):

    logging.debug('''provJava: action %s with parameters serverType:%s appConfigFilePath:%s 
    appContextPath:%s applicationType:%s filterType:%s filterPosition:%s instrumentationFilterClass:%s 
    filterMethod:%s''' % (action, serverType, appConfigFilePath, appContextPath, applicationType, filterType,
                         filterPosition, instrumentationFilterClass, filterMethod))

    if action == "prov":
         status = provision_java(serverType, appConfigFilePath, appContextPath, applicationType, filterType,
                                 filterPosition, instrumentationFilterClass, filterMethod)
         if status == True:
             logging.info("Success: provisioned java app %s" % appContextPath)
             return True
         else:
             error = "Failed: provisioned java app %s" % appContextPath
             logging.critical(error)
             return False
    elif action == "clean":
         status = unprovision_java(serverType, appConfigFilePath, appContextPath)
         if status == True:
             logging.info("Success: unprovisioned java app %s" % appContextPath)
             return True
         else:
             error = "Failed: provisioned java app %s" % appContextPath
             logging.critical(error)
             return False

    return False
