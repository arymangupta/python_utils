import logging
import os
import subprocess
import shutil
import tarfile
import sys
from autoprov.ProcessUtil import findOwner, findUid, findGid, createBkp, demote, report_ids, getCurrentUser

SHEBAND               = '^#!'
TAG                   = "iae_nodejs"
VSP_NODE_HOME         = "/opt/virsec/iae_nodejs"
PACKAGE_JSON          = "package.json"
PACKAGE_JSON_BKP      = "package.json.bkp"
RELATIVE_TAR_FILE_LOC = "misc/iae_nodejs_node_modules_v"
TAR_FILE_EXTENTION    = ".tar.gz"

def provNodejs(action, appDepFolder, startupConfFile, appCotext, nodeVersion):
    status = False
    if action == "prov":
        if appDepFolder is None or startupConfFile is None or appCotext is None or nodeVersion is None:
            error = "invalid arguments, some args are None"
            logging.critical(error)
            return False
        
        createBkp(os.path.join(VSP_NODE_HOME, PACKAGE_JSON),
                                                      os.path.join(VSP_NODE_HOME, PACKAGE_JSON_BKP))

        currentUser = getCurrentUser()
        fileOwner = None
        if not os.path.isfile(startupConfFile):
            error = "invalid startup script path %s" % startupConfFile
            logging.critical(error)
            return False
        fileOwner = findOwner(startupConfFile)
        logging.info("file owner is %s and current user is %s" % (fileOwner , currentUser))
        if fileOwner is currentUser:
            status = UpdateStartUpScript(appCotext, startupConfFile)
        # swith to file user and then call the update function
        else:
            ret = os.fork()
            if(ret == 0):
                demote(findUid(startupConfFile), findGid(startupConfFile))
                status = UpdateStartUpScript(appCotext, startupConfFile) 
                if status is False:
                    os._exit(1)
                os._exit(0)
            elif ret > 0:
                # Parent process waiting
                childProcExitInfo = os.wait()
                if childProcExitInfo[1] is not 0:
                    logging.critical("child failed updating required files")
                    status = False
                else:
                    logging.debug("Success, child  updated required files with status %d" % childProcExitInfo[1])
                    status = Untar(nodeVersion)
            else:
                logging.critical("faild creating child process")
                return False
    elif action == "clean":
        file = startupConfFile + ".unprov"
        if os.path.isfile(file):
            status = createBkp(file, startupConfFile)
            os.remove(file)
        status = True
    return status

def UpdateStartUpScript(appContext, startupConfFile):
    logging.info("updating file being %s having appcontext %s" % (startupConfFile, appContext))
    with open(startupConfFile, "r") as f:
        contents = f.readlines()
        if TAG in contents:
            logging.info("Virsec instrumentation for NodeJS is already configured")
            return True
        createBkp(startupConfFile, startupConfFile + ".unprov")
        toAdd = 'require("/opt/virsec/iae_nodejs")' + "('" + appContext + "');"
        if len(contents) > 0:
            logging.debug("Header of %s is %s" %(startupConfFile , contents[0]))
            index = 0;
            if SHEBAND in  contents[0]:
                index = 1;
            contents.insert(index, toAdd + '\n')
            logging.info("success added content %s at %s"  % (toAdd, index))
        else:
            contents = toAdd
            logging.warning("empty file, added content %s" % (contents))
        f.close()
        with open(startupConfFile, "w") as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
        
        return True
    logging.critical("Error: failed updating file %s" % startupConfFile)
    return False

def Untar(version):
    fileLoc = os.path.join(VSP_NODE_HOME, RELATIVE_TAR_FILE_LOC) + str(version) + TAR_FILE_EXTENTION
    logging.info("extracting tar file %s" % fileLoc)
    try:
        file = tarfile.open(fileLoc)
    except :
        logging.critical("There was an error opening tarfile. The file might be corrupt or missing.")
        return False

    try:
        file.extractall(VSP_NODE_HOME)
    except: 
        logging.critical("There was an error extracting tarfile. The file might be corrupt or missing.")
        return False

    file.close()
    logging.info("success extracting tar file %s" % fileLoc)
    return True

#provNodejs("clean","/home/pytuser/", "/home/pytuser/index.js", "testContext", 10)