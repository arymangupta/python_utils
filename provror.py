import os
import subprocess
import logging
import sys
import autoprov.ProcessUtil as ProcessUtil
from autoprov.ProcessUtil import *

logging.getLogger().setLevel(logging.DEBUG)
GEMFILE = "Gemfile"
GEMFILE_BKP = "Gemfile.backup"
PATTERN = "iae"
VSP_HOME = "/opt/virsec/iae-ruby"

def validate(applicationDepFolder, appContext):
    if applicationDepFolder is None  or appContext is None:
        error = "invalid arguments, some args are None"
        logging.critical(error)
        return False
    if not os.path.isdir(applicationDepFolder):
        error = "invalid app deployment folder %s" % applicationDepFolder
        logging.critical(error)
        return False
    fileName = os.path.join(applicationDepFolder, GEMFILE)
    if not os.path.isfile(fileName):
        error = "gem file is not present %s" % fileName
        logging.critical(error)
        return False
    return True

def provRor(action, applicationDepFolder, appContext):
    if validate(applicationDepFolder, appContext) is False:
        return False
    status = True
    fileName = os.path.join(applicationDepFolder, GEMFILE)
    fileOwner = findOwner(fileName)
    userId = findUid(fileName)
    userGid = findGid(fileName)
    env = os.environ.copy()
    currentUser = getCurrentUser()

    logging.info("file owner is %s and current user is %s" % (fileOwner , currentUser))
        # run provision being the file owner
    ret = os.fork()
    if(ret == 0):
        logging.debug("current child %d os path is %s" %(os.getpid(), os.getenv('PATH')))
        # set the path variable based on user of the gem file owner
        os.environ['PATH'] = GetPathVariable(fileOwner)
        os.environ['HOME'] = os.path.join('/home', fileOwner)
        logging.debug("current child home after is %s" % os.environ['HOME'])
        logging.debug("updated child os path is %s" % os.getenv('PATH'))
        demote(userId, userGid , True)
        if action == "prov":
            status = provisionRor(fileName, applicationDepFolder, appContext, False, userId, userGid) 
        elif action == "clean":
            status = unprovRor(applicationDepFolder, fileName, False, userId , userGid)
        if status is False:
            os._exit(1)
        os._exit(0)
    elif ret > 0:
        # Parent process waiting
        logging.debug("parent os path is %s" % os.getenv('PATH'))
        childProcExitInfo = os.wait()
        if childProcExitInfo[1] is not 0:
            # run provision being root user i.e current user
            logging.warning("child execution failed being user %s" % fileOwner)
            if action == "prov":
                status = provisionRor(fileName, applicationDepFolder, appContext, False, None, None)
            elif action == "clean":
                 status = unprovRor(applicationDepFolder, fileName, False, None, None)
            if status is False:
                # last option
                if action == "prov":
                    status = provisionRor(fileName, applicationDepFolder, appContext, True, None, None)
                elif action == "clean":
                    status = unprovRor(applicationDepFolder, fileName, True , None, None)
        else:
            logging.debug("child success provision with status %d being user %s" % (childProcExitInfo[1], fileOwner))
    else:
        logging.critical("faild creating child process")

    # fail secure for provision
    if status is False and action == "prov":
        # return value doesn't matter
        logging.info("fail secure, resason provision failed")
        unprovRor(applicationDepFolder, fileName)

    return status

def provisionRor(filename, applicationDepFolder, appContext, lookForEmbDir, userId = None, userGid=None):
    report_ids("provision execution stared")
    GEM_CMD = "gem"
    BUNDLE_CMD = "bundle"
    CD = "cd " + applicationDepFolder + " && "
    if isWritable(filename) is False:
        error = "gem file %s is not writable" % filename
        logging.critical(error)
        return False

    with open(filename, 'r') as f:
        contents = f.readlines()
        if PATTERN in contents:
            logging.info("already provisioned")
            return True
        f.close()

    status, GEM_CMD, BUNDLE_CMD = getGemBundleCommand(lookForEmbDir, applicationDepFolder)
    if status is False:
        return False

    logging.info("bundle and gem command being used for provision are %s %s" % (BUNDLE_CMD, GEM_CMD))
    
    #if userId is not None and userGid is not None:
    #    demote(userId, userGid, False)
    #else:
    #    logging.info("demotion skipped--->>>>>>>>>>>>>>REMOVE")

    # get install direcotry
    installDir = None
    command = CD + BUNDLE_CMD + " list --paths | head -n 1"
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        logging.warning("error getting emb dir %s" % stderr)
    else:
        installDir = str(stdout).replace("\n", "")
        logging.info("got install directory as %s" % installDir)

    gemCommand = CD + GEM_CMD + " install --force --local "
    if installDir is not None:
        installDir = splitPath(installDir, 2)
        gemCommand = gemCommand + "--install-dir " + installDir

    logging.info("final command is %s" % gemCommand)

    # take backup of Gemfile
    createBkp(filename,os.path.join(applicationDepFolder, GEMFILE_BKP))

    # install if not present iae gems
    command =  "grep iae " + filename
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        command = gemCommand + " " + os.path.join(VSP_HOME, "iae-4.2.0.gem")
        rc,stdout,stderr = executeCommand(command)
        if rc is not 0:
            logging.warning("Unable to install iae gem %s" % stderr)
            return False
    else:
        if len(stdout) > 0:
            logging.info("iae gem already present in %s i.e already provisioned" % filename)
            return True

    # append this to gem file,
    command =  "sed -i " +  "\"$ a gem 'iae'\" " + filename
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        logging.warning("failed adding $ a gem 'iae' to %s error %s" % (filename, stderr))
    else:
        logging.info("success, added $ a gem 'iae' to %s" % filename)

    # install if not present httparty
    installGem(gemCommand, filename, "httparty", "httparty-0.16.3.gem")

    # install if not present ffi
    installGem(gemCommand, filename, "ffi", "ffi-1.9.25.gem")

    # install if not present jwt
    installGem(gemCommand, filename, "jwt", "jwt-2.1.0.gem")

    # install if not present mime-types
    installGem(gemCommand, filename, "mime-types", "mime-types-3.2.2.gem")

    # install if not present mime-types-data
    installGem(gemCommand, filename, "mime-types-data", "mime-types-data-3.2018.0812.gem")

    # install if not present multi_xml
    installGem(gemCommand, filename, "multi_xml", "multi_xml-0.6.0.gem")

    # install if not present google-protobuf
    installGem(gemCommand, filename, "google-protobuf", "google-protobuf-3.17.3-x86_64-linux.gem" , True)

    # removing the symbole may not be required in python
    removeShellSymbol(filename)

    # check if bundle config file is present or not
    checkBundleConfig(applicationDepFolder, BUNDLE_CMD, installDir)

    # execute bundle command, bundle install
    if executeBundle(CD, BUNDLE_CMD) is False:
        return False

    # create app context file
    crateAppContextFile(applicationDepFolder, appContext)

    return True

def unprovRor(applicationDepFolder, gemFile, lookForEmbDir = False , userId = None, userGid=None):
    report_ids("unprovision execution stared, cleaning up state")
    CD = "cd " + applicationDepFolder + " && "
    # copy the backup file to original Gemfile
    gemFileBkp = os.path.join(applicationDepFolder, GEMFILE_BKP)
    if os.path.isfile(gemFileBkp):
        createBkp(gemFileBkp, gemFile)
    else:
        logging.debug("no backup file is present")
    #os.remove(gemFileBkp)

    # remove the app context file
    contexFile = os.path.join(applicationDepFolder, "vsp-context.txt")
    if os.path.isfile(contexFile):
        os.remove(contexFile)

    #if userId is not None and userGid is not None:
    #    demote(userId, userGid, False)

    # find the gem and bundle command
    status, GEM_CMD, BUNDLE_CMD = getGemBundleCommand(lookForEmbDir, applicationDepFolder)
    if status is False:
        return False
    logging.info("bundle and gem command being used for unprovision are %s %s" % (BUNDLE_CMD, GEM_CMD))

    # bundle uninstall
    if executeBundle(CD, BUNDLE_CMD) is False:
        return False

    return True

def installGem(gemCommand, filename , gemName, gemFile, needSed = False):
    command =  "grep " + gemName + " " + filename
    rc, stdout, stderr = executeCommand(command)
    if rc is not 0:
        command = gemCommand + " " + os.path.join(VSP_HOME, gemFile)
        rc,stdout,stderr = executeCommand(command)
        if rc is not 0:
            logging.warning("Unable to install %s gem %s" % (gemName, stderr))
            return False
        else:
            if needSed:
                command = "sed -i " +  "\"$ a gem '" + gemName + "'\" " + filename
                rc, stdout, stderr = executeCommand(command)
                if rc is not 0:
                    logging.warning("failed adding $ a gem '%s' to %s error %s" % (gemName, filename, stderr))
                else:
                    logging.info("success, added $ a gem '%s' to %s" % (gemName, filename))
    else:
        if len(stdout) > 0:
            logging.debug("%s gem already present in %s" % (gemNamem, filename))
    return True

def removeShellSymbol(filename):
    command = "sed -i " +  "\"s/\r//g\" " + filename
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        logging.warning("failed removed 's/\r//g' from %s error %s" % (filename, stderr))
    else:
        logging.debug("success, removed 's/\r//g' from %s" % filename)

def checkBundleConfig(applicationDepFolder, BUNDLE_CMD, installDir):
    confileLoc = os.path.join(applicationDepFolder, "bundle/config")
    if installDir is not None and "vendor/bundle" in installDir:
        if os.path.isfile(confileLoc):
            with open(confileLoc, "r") as f:
                contents = f.readlines()
                f.close()
                command = "cat " + os.path.join(applicationDepFolder, "bundle/config") + " | grep BUNDLE_DEPLOYMENT"
                rc, stdout, stderr = executeCommand(command)
                if rc is not 0:
                    logging.warning("failed executing %s" % command)
                else:
                    logging.info("success executed %s" % command)
                    if "true" in stdout:
                        if "BUNDLE_PATH" in contents:
                            logging.info("Path already set for deployment mode")
                        else:
                            command = BUNDLE_CMD + " config set path vendor/bundle"
                            rc, stdout, stderr = executeCommand(command)
                            if rc is not 0:
                                logging.warning("failed executing %s" % command)
                            else:
                                logging.info("success executed %s" % command)
        else:
            logging.debug("file location %s is not found" % confileLoc)
    else:
        if installDir is not None:
            logging.debug("vendor/bundle is not found in %s" % installDir)
        else:
            logging.debug("installDir is none")

def crateAppContextFile(applicationDepFolder, appContext):
    file = os.path.join(applicationDepFolder, "vsp-context.txt")
    command = "echo " + appContext + " > " + file
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        logging.warning("Unable to cretae file %s" % file)
    else:
        logging.info("Saved %s in file %s" % (appContext, file))

def executeBundle(CD, BUNDLE_CMD):
    command = CD + BUNDLE_CMD + " config unset deployment"
    rc,stdout,stderr = executeCommand(command)
    command = CD + BUNDLE_CMD + " install --local"
    rc,stdout,stderr = executeCommand(command)
    if rc is not 0:
        return False
    else:
        logging.info("success executed %s" % command)
    return True

def getGemBundleCommand(lookForEmbDir, applicationDepFolder):
    GEM_CMD = "gem"
    BUNDLE_CMD = "bundle"
    commandGem = "command -v " + GEM_CMD
    commandBundle = "command -v " + BUNDLE_CMD
    if lookForEmbDir is False:
        if executeCommand(commandGem)[0] is not 0 or executeCommand(commandBundle)[0] is not 0:
            error = "%s or %s is not found" % (GEM_CMD, BUNDLE_CMD)
            logging.critical(error)
            return False, None, None
    else:
        logging.info("looking for embeded gem dir")
        command = "find " + applicationDepFolder + " -name gem | head -n 1"
        rc,stdout,stderr = executeCommand(command)
        if rc is not 0:
            logging.warning("error getting emb dir %s" % stderr)
            return False, None, None
        stdout = str(stdout).replace(GEM_CMD, "").replace("\n", "")
        logging.debug("output of getting emb dir %s" % stdout)
        GEM_CMD = os.path.join(stdout, "gem")
        BUNDLE_CMD = os.path.join(stdout, "bundle")
    return True, GEM_CMD, BUNDLE_CMD

