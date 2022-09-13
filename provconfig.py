import sys
import os
import autoprov.ProcessUtil as ProcessUtil
import logging

APPLICATION_JAVA       =  "java"
APPLICATION_DNET       =  [".net",".net core", "dotnet", "dnet"]
APPLICATION_PHP        =  "php"
APPLICATION_NODEJS     = ["node.js", "nodejs", "node"]
APPLICATION_RUBY       = ["ruby", "ror"]
EWAF_SERVER_TYPE       = ["nginx", "apache httpd", "iis", "apache", "httpd", "apache2"]
APPLICATION_IAE_ENCODE = ["iae-encode", "iaeencode"]
SUPPORTED_LOG_LEVEL    = ["info", "debug", "warn", "trace", "off", "on" , "error", "warning", "information"]

# below string are take from json_msg_def.h of CVE-Assist source
EDIT_FIELD_LOG_PATH    = "logPath"
EDIT_FIELD_LOG_LEVEL   = "logLevel"

VSP_HOME_LINUX      = "/opt/virsec/"
VSP_HOME_WINDOWS    = "C:\\Program Files (x86)\\Virsec"
VSP_HOME = VSP_HOME_LINUX

# relative conf file location for each process type
# php is excetion as it's conf file is present in web root 
IAE_JAVA         = "iae-java"
IAE_DNET         = "iae-dnet"
IAE_NODEJS       = "iae_nodejs"
IAE_PHP          = "iae-php"
IAE_ROR          = "iae-ruby"
IAE_EWAF         = "config"
IAE_ENCODE       = "config"
CONFIG           = "config"

# below macros are used to find entry/line that need to edited for respective process type

JAVA_CONFIG_PREFIX                    = "logging"
JAVA_CONFIG_EXT                       = ".properties"
JAVA_CONFIG_EDIT_ENTRY_LOG_PATH       = "logging."
JAVA_CONFIG_EDIT_ENTRY_LOG_LEVEL      = "level"

DNET_CONFIG_PREFIX                    = "vsp"
DNET_CONFIG_EXT                       = ".cfg"
DNET_CONFIG_EDIT_ENTRY_LOG_PATH       = "LogPath"
DNET_CONFIG_EDIT_ENTRY_LOG_LEVEL      = "LogLevel"

PHP_CONFIG_PREFIX                     = "VirsecIae"
PHP_DEFAULT_CONFIG_PREFIX             = "iae-php"
PHP_CONFIG_EXT                        = ".config"
PHP_CONFIG_EDIT_ENTRY_LOG_PATH        = "logPath"
PHP_CONFIG_EDIT_ENTRY_LOG_LEVEL       = "logLevel"

NODEJS_CONFIG_PREFIX                  = "logger"
NODEJS_CONFIG_EXT                     = ".yml"
NODEJS_CONFIG_EDIT_ENTRY_LOG_PATH     = "log_file_path"
NODEJS_CONFIG_EDIT_ENTRY_LOG_LEVEL    = "log_level"
#NODEJS_CONFIG_DEPLOY_ENV              = "development"


ROR_CONFIG_PREFIX                     = "logger"
ROR_CONFIG_EXT                        = ".yml"
ROR_CONFIG_EDIT_ENTRY_LOG_PATH        = "log_file_path"
ROR_CONFIG_EDIT_ENTRY_LOG_LEVEL       = "log_level"

EWAF_CONFIG_PREFIX                    = "ewaf"
EWAF_CONFIG_EXT                       = ".cfg"
EWAF_CONFIG_EDIT_ENTRY_LOG_PATH       = "logPath"
EWAF_CONFIG_EDIT_ENTRY_LOG_LEVEL      = "logLevel"


IAE_ENCODE_CONFIG_PREFIX                    = "iae_encode"
IAE_ENCODE_CONFIG_EXT                       = ".cfg"
IAE_ENCODE_CONFIG_EDIT_ENTRY_LOG_PATH       = "logPath"
IAE_ENCODE_CONFIG_EDIT_ENTRY_LOG_LEVEL      = "logLevel"

PARAM_COUNT = 7

DELIMETER = ":"
ENCODING = "utf-8"

def updateConfFile(processType, contextPath, editField, deploymentFolder, restartCmd):
    setVspHome()
    processType = processType.lower()
    logging.info("Trying to update config for process type %s, having context %s, field to edit %s, deploymentFolder %s restartCom %s" 
           % (processType, contextPath, editField, deploymentFolder, restartCmd))

    key = getEditFieldKey(editField)
    value = getEditFieldValue(editField)
    if checkLogLvlValidity(key, value) == False:
        error = "Invalid " + key + " " + value
        sys.exit(error)

    if processType in APPLICATION_JAVA:
        return updateConfJava(contextPath, editField, deploymentFolder)

    elif processType in APPLICATION_DNET:
        return updateConfDotNet(contextPath, editField, deploymentFolder)

    elif processType in APPLICATION_PHP:
        return updateConfPhp(contextPath, editField, deploymentFolder)

    elif processType in APPLICATION_NODEJS:
        return updateConfNodejs(contextPath, editField, deploymentFolder)

    elif processType in APPLICATION_RUBY:
        return updateConfRor(contextPath, editField, deploymentFolder)

    elif processType in EWAF_SERVER_TYPE:
        return updateConfEwaf(restartCmd, editField)

    elif processType in APPLICATION_IAE_ENCODE:
        return updateConfIaeEncode(contextPath, editField)
    
    else:
        error = "WARN: unsupported processType " + processType
        sys.exit(error)

# Java
def updateConfJava(contextPath, editField, deploymentFolder):
    writeFile = False
    VSP_HOME = setVspHome()
    dirLoc = os.path.join(VSP_HOME, IAE_JAVA)
    fileLocDefault = os.path.join(dirLoc, JAVA_CONFIG_PREFIX + JAVA_CONFIG_EXT)
    logging.debug("deafult file location %s" % fileLocDefault)
    cstmFileLoc = os.path.join(dirLoc, JAVA_CONFIG_PREFIX + "-" + contextPath + JAVA_CONFIG_EXT)
    confFileLoc = ""
    logging.debug("custom file location %s" % cstmFileLoc)
    if (os.path.isfile(cstmFileLoc)):
        logging.debug("using custom file location %s" % cstmFileLoc)
        confFileLoc = cstmFileLoc
    else:
        if(len(contextPath) == 0):
            logging.debug("Info:using default conf file location %s" % fileLocDefault)
            confFileLoc = fileLocDefault
        else:
            logging.info("skipped updating default conf file location %s" % fileLocDefault)
            return False

    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            searchKey = JAVA_CONFIG_EDIT_ENTRY_LOG_LEVEL
            if EDIT_FIELD_LOG_PATH in key:
                searchKey = JAVA_CONFIG_EDIT_ENTRY_LOG_PATH + ProcessUtil.getOsName()
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = JAVA_CONFIG_EDIT_ENTRY_LOG_PATH + JAVA_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            for index, line in enumerate(contents):
                if  searchKey in line:
                    logging.debug("content to update %s" % contents[index])
                    #logging.level=INFO or #logging.windows.directory=${VSP_HOME}/log/iae-java
                    contents[index] = contents[index].split("=", 1)[0]
                    contents[index] = contents[index] + "=" + value + "\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False

    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents)
    return True

# .Net, .Net Core
def updateConfDotNet(contextPath, editField, deploymentFolder):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_DNET)
    fileLocDefault = os.path.join(dirLoc, DNET_CONFIG_PREFIX + DNET_CONFIG_EXT)
    logging.debug("deafult file location %s" % fileLocDefault)
    cstmFileLoc = os.path.join(deploymentFolder, DNET_CONFIG_PREFIX + DNET_CONFIG_EXT)
    confFileLoc = None
    logging.debug("custom file location %s" % cstmFileLoc)
    if (os.path.isfile(cstmFileLoc)):
        logging.debug("using custom file location %s" % cstmFileLoc)
        confFileLoc = cstmFileLoc
    else:
        #use default file location
        if(len(contextPath) == 0):
            logging.info("using default conf file location %s" % fileLocDefault)
            confFileLoc = fileLocDefault
        else:
            logging.info("Skipped updating default conf file location %s" % fileLocDefault)
            return False
   
    contents = ProcessUtil.readFile(confFileLoc, ENCODING)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            searchKey = None 
            if EDIT_FIELD_LOG_PATH in key:
                searchKey = DNET_CONFIG_EDIT_ENTRY_LOG_PATH
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = DNET_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            for index, line in enumerate(contents):
                if  searchKey != None and searchKey.lower() in line.lower():
                    logging.debug("content to update %s" % contents[index])
                    #logging.level=INFO or #logging.windows.directory=${VSP_HOME}/log/iae-java
                    addComma = checkComma(line)
                    contents[index] = contents[index].split(":", 1)[0]
                    contents[index] = contents[index] + ": \"" + value + "\""
                    if(addComma):
                        contents[index] = contents[index] + ","
                    contents[index] = contents[index] + "\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True

# Php
def updateConfPhp(contextPath, editField, deploymentFolder):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_PHP)
    fileLocDefault = os.path.join(dirLoc, PHP_DEFAULT_CONFIG_PREFIX + PHP_CONFIG_EXT)
    logging.debug("deafult file location %s" % fileLocDefault)
    cstmFileLoc = os.path.join(deploymentFolder,  PHP_CONFIG_PREFIX + PHP_CONFIG_EXT)
    confFileLoc = None
    if (os.path.isfile(cstmFileLoc)):
        logging.debug("using custom file location %s" % cstmFileLoc)
        confFileLoc = cstmFileLoc
    else:
        #use default file location
        if(len(contextPath) == 0):
            logging.debug("Info:using default conf file location %s" % fileLocDefault)
            confFileLoc = fileLocDefault
        else:
            logging.info("skipped updating default conf file location %s" % fileLocDefault)
            return True

    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            for index, line in enumerate(contents):
               if key.lower() in line.lower():
                    # LogLevel Trace or LogPath /var/virsec/php
                    logging.debug("content to update %s" % contents[index])
                    dest = value
                    src = line.split(" ")[1]
                    contents[index] = contents[index].replace(src, dest) + "\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True

# Node.js
def updateConfNodejs(contextPath, editField, deploymentFolder):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_NODEJS)
    dirLoc = os.path.join(dirLoc, CONFIG)
    fileLocDefault = os.path.join(dirLoc, NODEJS_CONFIG_PREFIX + NODEJS_CONFIG_EXT)
    logging.debug("deafult file location %s" % fileLocDefault)
    cstmFileLoc = os.path.join(dirLoc, NODEJS_CONFIG_PREFIX + "." + contextPath + NODEJS_CONFIG_EXT)
    confFileLoc = None
    logging.debug("custom file location %s" % cstmFileLoc)
    if (os.path.isfile(cstmFileLoc)):
         logging.debug("using custom file location %s" % cstmFileLoc)
         confFileLoc = cstmFileLoc
    else:
        #use default file location
        #if(len(contextPath) == 0):
        logging.debug("using default conf file location %s" % fileLocDefault)
        confFileLoc = fileLocDefault
        #else:
         #   print("Info:Skipped updating default conf file location %s" % fileLocDefault)
         #   return
    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            searchKey = NODEJS_CONFIG_EDIT_ENTRY_LOG_LEVEL 
            if EDIT_FIELD_LOG_PATH in key:
                searchKey = NODEJS_CONFIG_EDIT_ENTRY_LOG_PATH
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = NODEJS_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            startIndex = 0
#            for index, line in enumerate(contents):
#                if NODEJS_CONFIG_DEPLOY_ENV in line:
#                    startIndex = index
#                    break
            for index in range(startIndex, len(contents)):
                if searchKey in contents[index]:
                    logging.debug("content to update %s" % contents[index])
                    #  log_path: '/var/virsec/log/iae_nodejs/iae-nodejs.log'
                    # log_level: 'info'
                    contents[index] = contents[index].split(":", 1)[0]
                    contents[index] = contents[index] + ": '" + value + "'\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
#                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True

# Ruby
def updateConfRor(contextPath, editField, deploymentFolder):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_ROR)
    fileLocDefault = os.path.join(dirLoc, ROR_CONFIG_PREFIX + ROR_CONFIG_EXT)
    logging.debug("deafult file location %s" % fileLocDefault)
    cstmFileLoc = os.path.join(dirLoc, ROR_CONFIG_PREFIX + "-" + contextPath + ROR_CONFIG_EXT)
    confFileLoc = ""
    logging.debug("custom file location %s" % cstmFileLoc)
    if (os.path.isfile(cstmFileLoc)):
        logging.debug("using custom file location %s" % cstmFileLoc)
        confFileLoc = cstmFileLoc
    else:
        #use default file location
        if(len(contextPath) == 0):
            logging.debug("using default conf file location %s" % fileLocDefault)
            confFileLoc = fileLocDefault
        else:
            logging.info("skipped updating default conf file location %s" % fileLocDefault)
            return False

    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            searchKey = ROR_CONFIG_EDIT_ENTRY_LOG_PATH + ROR_CONFIG_EDIT_ENTRY_LOG_LEVEL 
            if EDIT_FIELD_LOG_PATH in key:
                searchKey = ROR_CONFIG_EDIT_ENTRY_LOG_PATH
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = ROR_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            for index, line in enumerate(contents):
                if  searchKey in line:
                    logging.debug("content to update %s" % contents[index])
                    #logging.level=INFO or #logging.windows.directory=${VSP_HOME}/log/iae-java
                    contents[index] = contents[index].split(":", 1)[0]
                    if(searchKey in ROR_CONFIG_EDIT_ENTRY_LOG_LEVEL):
                        contents[index] = contents[index] + ": Logger::" + value.upper() + "\n"
                    else:
                       contents[index] = contents[index] + ": '" + value + "'\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True


# Nginx, Apache Httpd
def updateConfEwaf(restartcmd, editField):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_EWAF)
    confFileLoc = os.path.join(dirLoc, EWAF_CONFIG_PREFIX + EWAF_CONFIG_EXT)
    logging.debug("conf file location %s" % confFileLoc)
    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            if EDIT_FIELD_LOG_PATH in key:
                searchKey = EWAF_CONFIG_EDIT_ENTRY_LOG_PATH
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = EWAF_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            for index, line in enumerate(contents):
                if searchKey != None and searchKey in line:
                    logging.debug("content to update %s" % contents[index])
                    addComma = checkComma(line)
                    contents[index] = contents[index].split(":", 1)[0]
                    contents[index] = contents[index] + ":" + " \"" + value + "\""
                    if(addComma):
                        contents[index] = contents[index] + ","
                    contents[index] = contents[index] + "\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True


# Iae Encode
def updateConfIaeEncode(contextPath, editField):
    writeFile = False
    dirLoc = os.path.join(VSP_HOME, IAE_ENCODE)
    confFileLoc = os.path.join(dirLoc, IAE_ENCODE_CONFIG_PREFIX + IAE_ENCODE_CONFIG_EXT)
    logging.debug("conf file location %s" % confFileLoc)
    contents = ProcessUtil.readFile(confFileLoc)
    if contents != None:
        key = getEditFieldKey(editField)
        value = getEditFieldValue(editField)
        logging.debug("key %s and vlaue %s" % (key,value))
        if key != None and value != None:
            searchKey = None
            if EDIT_FIELD_LOG_PATH in key:
                # eg "LogPath": "/var/log/nginx",
                searchKey = IAE_ENCODE_CONFIG_EDIT_ENTRY_LOG_PATH
            elif EDIT_FIELD_LOG_LEVEL in key:
                searchKey = IAE_ENCODE_CONFIG_EDIT_ENTRY_LOG_LEVEL
            logging.debug("serach key is %s" % searchKey)
            for index, line in enumerate(contents):
                if searchKey != None and searchKey in line:
                    logging.debug("content to update %s" % contents[index])
                    addComma = checkComma(line)
                    contents[index] = contents[index].split(":", 1)[0]
                    contents[index] = contents[index] + ":" + " \"" + value + "\""
                    if(addComma):
                        contents[index] = contents[index] + ","
                    contents[index] = contents[index] + "\n"
                    logging.info("Success: update content to %s" % contents[index])
                    writeFile = True
                    break
        else:
            logging.warning("key and value are not present")
            return False
    else:
        logging.warning("not able to read contents")
        return False
    
    if(writeFile):
        ProcessUtil.writeFile(confFileLoc, contents, ENCODING)
    return True


def getEditFieldValue(editField):
    if DELIMETER not in editField:
        return None
    editValue = editField.split(DELIMETER, 1)[1]
    return editValue

def getEditFieldKey(editField):
    if DELIMETER not in editField:
        return None
    editValue = editField.split(DELIMETER, 1)[0]
    return editValue
    
def setVspHome():
    if "windows" in ProcessUtil.getOsName():
        VSP_HOME = VSP_HOME_WINDOWS
    elif "linux" in ProcessUtil.getOsName():
        VSP_HOME = VSP_HOME_LINUX
    logging.debug("updated vsp home as %s" % VSP_HOME)
    return VSP_HOME

def getServerName(restartCmd):
    logging.debug("getting server name using %s" % restartCmd)
    if "apache2" in restartCmd:
        return "apache2"
    if "httpd" in restartCmd:
        return "httpd"
    if "openresty" in restartCmd:
        return "openresty"
    if "nginx" in restartCmd:
        return "nginx"
    return None

def checkComma(string):
    if ',' in string:
        return True
    return False

def checkLogLvlValidity(key, value):
    if key.lower() in "loglevel":
        if value.lower() in SUPPORTED_LOG_LEVEL:
            return True
        return False
    return True