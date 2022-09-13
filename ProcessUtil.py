import subprocess
import sys
import platform
import os
import logging
import shutil

def getOsName():
    return platform.system().lower()

if getOsName().startswith('win') is False:
    import pwd
using_distro = False
try:
    import distro
    using_distro = True
except ImportError:
    pass

LD_CONF_FILE = "virsec_lua.conf"
SWITCH_USER_CMD = "su -l "
SUFFIX_CMD = " -c 'bash -i -c 'env''"
PATH = "PATH="
def execute(*args, **kwargs):
    if "check_output" in dir(subprocess):
        output = ""
        try:
            output = subprocess.check_output(*args, **kwargs)
        except subprocess.CalledProcessError as error:
            return error.output
        return output

    process = subprocess.Popen(stdout=subprocess.PIPE, *args, **kwargs)
    output, unused_err = process.communicate()
    ret = process.poll()
    if ret:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = args[0]
        error = subprocess.CalledProcessError(ret, cmd)
        error.output = output
        raise error
    return output

def restartWebserver(webServer):
    distribution = ""
    if using_distro:
        distribution = distro.linux_distribution()[0].lower()
        logging.debug("using distro OS: %s" % (distribution))
    else:
        distribution = platform.linux_distribution()[0].lower()
        logging.debug("using platform OS: %s" % (distribution))
    if webServer == "Apache":
        if "ubuntu" in distribution and commandExist("service"):
            if commandExist("apache2"):
                logging.debug(execute("service apache2 restart", shell=True))
                logging.info("Success apache: executed service apache2 restart")
                return True
            else:
                print("Warn apache: command not exist sudo service apache2 restart")
        elif "red" in distribution or "centos" in distribution:
            if commandExist("httpd") and commandExist("service"):
                logging.debug(execute("service httpd restart", shell=True))
                logging.info("Success apache: executed service httpd restart")
                return True
            else:
                logging.warning("apache: command not exist service httpd restart")

    if webServer == "Nginx":
        if commandExist("nginx") and commandExist("systemctl"):
            logging.debug(execute("systemctl restart nginx", shell=True))
            logging.info("Success apache: systemctl restart nginx")
            return True
        else:
            logging.warning("apache: command not exist systemctl restart nginx")

    return False

def restartPhp(webServer, phpVersion):
    distribution = ""
    if using_distro:
        distribution = distro.linux_distribution()[0].lower()
        logging.debug("using distro OS: %s" % (distribution))
    else:
        distribution = distro.linux_distribution()[0].lower()
        logging.debug("using platform OS: %s" % (distribution))
    if webServer == "Apache":
        if "ubuntu" in distribution:
            restartWebserver(webServer)
            if phpProcessExist("php"+phpVersion+"-fpm"):
                logging.debug(execute("service php"+phpVersion+"-fpm restart", shell=True))
                logging.info("Success apache: service php%s-fpm restart" % phpVersion)
            else:
                logging.warning("Warn apache: command not exist sudo service php%s-fpm restart" % phpVersion)

        elif "red" in distribution or "centos" in distribution:
            restartWebserver(webServer)
            if phpProcessExist("php-fpm"):
                logging.debug(execute("service php-fpm restart", shell=True))
                logging.info("Success apache: service php-fpm restart")
            else:
                logging.warning("Warn apache: command not exist service php-fpm restart")

    if webServer == "Nginx":
        if "ubuntu" in distribution:
            restartWebserver(webServer)
            if phpProcessExist("php"+phpVersion+"-fpm"):
                logging.debug(execute("service php"+phpVersion+"-fpm restart", shell=True))
                logging.info("Success apache: service php%s-fpm restart" % phpVersion)
            else:
                logging.warning("Warn apache: command not exist service php%s-fpm restart" % phpVersion)

        elif "red" in distribution or "centos" in distribution:
            restartWebserver(webServer)
            if phpProcessExist("php-fpm"):
                logging.debug(execute("service php-fpm restart", shell=True))
                logging.info("Success apache: service php-fpm restart")
            else:
                logging.warning("apache: command not exist service php-fpm restart" )

def findConfLocation(webServer , restartCmd):
    output = "None"
    if webServer == "Apache":
        restartCmd = restartCmd
        if "apache2" in restartCmd:
             output = parseApcaheOutput(execute("apache2ctl -V", shell=True, stderr=subprocess.STDOUT))
        elif "httpd" in restartCmd:
             output = parseApcaheOutput(execute("httpd -V", shell=True, stderr=subprocess.STDOUT))
        else:
           logging.warning("restart command is not correct %s" % restartCmd)            
    elif webServer == "Nginx":
        restartCmd = restartCmd
        if "nginx" in restartCmd:
            output = parseNginxOutput(execute("nginx -t", shell=True, stderr=subprocess.STDOUT))
        elif "openresty" in restartCmd:
            output = parseNginxOutput(execute("openresty -t", shell=True, stderr=subprocess.STDOUT))
        else:
            logging.warning("restart command is not correct %s" % restartCmd)
    
    if not os.path.isfile(output):
      logging.warning("Configuration file %s is not present" % output)
      return "None"
    return output

def parseNginxOutput(output):
    ret = "None"
    output = output.decode()
    for word in output.split():
        if ".conf" in word:
            ret = word
            break
    print("Found config path %s" % ret)
    return ret

def parseApcaheOutput(output):
    ret = "None"
    output = output.decode()
    osName = getDistributionName()
    if "alpine" in osName:
        logging.info("found alpine as os name, skipp using HTTPD_ROOT to get the conf file location")
        ret = ""
    for word in output.split():
        if "HTTPD_ROOT" in word and not "alpine" in osName:
            word = word.replace("HTTPD_ROOT", "")
            word = word.replace("=", "")
            word = word.replace('"', "")
            ret = word
        elif "SERVER_CONFIG_FILE" in word:
            word = word.replace("SERVER_CONFIG_FILE", "")
            word = word.replace("=", "")
            word = word.replace('"', "")
            ret = ret + '/' + word
    logging.debug("Found config path %s" % ret)
    return ret

def commandExist(command):
    rc = subprocess.call(['which', command],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT)
    if rc == 0:
      return True
    else:
       return False
    return False

def phpProcessExist(processName):
    if commandExist("systemctl") and commandExist("grep"):
        name = execute("systemctl list-unit-files | grep "+processName, shell=True, stderr=subprocess.STDOUT)
        name = name.decode('utf8')
        if processName in name:
            logging.info("Success: process found %s" % processName)
            return True
        else:
            logging.warning("process not found %s" % processName)
    #add some logic in case the above commands are not found
    else:
        return False
    return False

def selinuxLoadAndCompilePolicyModule(action):
    output = ""
    if commandExist("getenforce"):
        if commandExist("semodule") and commandExist("chcon"):
            if action == "prov":
                output = execute("semodule -i /opt/virsec/data/selinux_policy/virsec.pp", shell = True, stderr=subprocess.STDOUT)
                if checkForErrorInOutput(output) == False:
                    logging.info("success selinux: executed semodule -i /opt/virsec/data/selinux_policy/virsec.pp")
                output = execute("chcon -t virsec_log_t /var/virsec/ -R", shell = True, stderr=subprocess.STDOUT)
                output = execute("chcon -t virsec_log_t /vspstats -R", shell = True, stderr=subprocess.STDOUT)
                output = execute("chcon -t init_exec_t /opt/virsec/bin -R", shell = True, stderr=subprocess.STDOUT)
                if checkForErrorInOutput(output) == False:
                    logging.info("success selinux: execute chcon -t virsec_log_t /vspstats -R")
                    logging.info("success selinux: execute chcon -t virsec_log_t /var/virsec/ -R")
                    logging.info("success selinux: execute chcon -t int_exec_t /opt/virsec/bin -R")
                # this is the other way to use httpd predefined type to lable the directory which can be read and rwrite
                #output = execute("chcon -t httpd_sys_rw_content_t /vspstats -R", shell = True)
            elif action == "clean":
                output = execute("semodule -r virsec", shell = True, stderr=subprocess.STDOUT)
                if checkForErrorInOutput(output) == False:
                    logging.info("success selinux: executed semodule -r virsec")
                # no need of chcon the vspstats directory will be relabeld to default_t by selinux infra automatically
        else:
            logging.info("selinux: command not present, semodule or chcon")
    else:
        logging.info("Info selinux: getenforce command is not present in the system, skipped adding selinux virsec module")
    return output

# This function will be used in future
def runSelinuxApplyPolicyShellScript(action):
    output = ""
    if commandExist("getenforce"):
         if action == "prov":
             output = execute("/opt/virsec/bin/selinux/applyVirsecPolicy.sh", shell = True)
         elif action == "clean":
             output = execute("/opt/virsec/bin/selinux/applyVirsecPolicy.sh clean", shell = True)
    return output

def checkForErrorInOutput(output):
    if type(output) != str:
        output = output.decode()
    if "failed" in output.lower()  or "error" in output.lower():
        return True
    return False


# TODO: improve logic to get the os distribution name correctly
def getDistributionName():
    distribution = "None"
    if using_distro:
        distribution = distro.linux_distribution()[0].lower()
        logging.debug("using distro OS: %s" % (distribution))
    else:
        distribution = platform.linux_distribution()[0].lower()
        logging.debug("using platform OS: %s" % (distribution))
    print("Info: distribution %s" % distribution) 
    if "red" in distribution or "centos" in distribution:
       return "rhel"
    elif "ubuntu" in distribution:
       return "ubuntu"
    elif "alpine" in distribution:
        return "alpine"
    elif "debian" in distribution:
        return "debian"
    return distribution.rstrip()

def getDistributionVersion():
    version = "0"
    if using_distro:
        version = distro.linux_distribution()[1].lower()
        logging.debug("using distro OS version: %s" % (version))
    else:
        version = platform.linux_distribution()[1].lower()
        logging.debug("using platform OS version: %s" % (version))
    print("Info: distribution version %s" % version)
    return str(int(float(version.rstrip())))

def getNginxVersion():
    output = "None"
    if commandExist("nginx"):
        output = execute("nginx -v", shell=True, stderr=subprocess.STDOUT)
        output = output.decode()
        # output example of nginx -v 
        # nginx version: nginx/1.14.1 (ubuntu)
        output = output.replace("nginx version: nginx/", "")
        # check if there are any sapce 1.14.1 (ubuntu)
        output = output.split()[0]
        print("Info: nginx version: %s" % output)
        return output.rstrip()
    logging.warning("command nginx is not present")
    return output

def testConfFile(webServer, restartCmd):
    output = "None"
    restartCmd = "nginx"
    if webServer == "Apache":
        restartCmd = sys.argv[4].lower()
        if "apache2" in restartCmd:
             output = execute("apache2ctl -t", shell=True, stderr=subprocess.STDOUT)
        elif "httpd" in restartCmd:
             output = execute("httpd -t", shell=True, stderr=subprocess.STDOUT)
        else:
            logging.critical("restart command is not correct %s" % restartCmd)
            return False            
    elif webServer == "Nginx":
        if "nginx" in restartCmd:
            output = execute("nginx -t", shell=True, stderr=subprocess.STDOUT)
        elif "openresty" in restartCmd:
            output = execute("openresty -t", shell=True, stderr=subprocess.STDOUT)
        else:
            logging.critical("restart command is not correct %s" % restartCmd)
            return False
            
    if checkForErrorInOutput(output):
        return False
    return True

def updatePathVariable():
    path =  os.environ.get('PATH').split(':')
    if '/usr/sbin' not in path:
        os.environ["PATH"] += os.pathsep + '/usr/sbin'
        logging.debug("Added Path /usr/sbin")
    if '/usr/bin' not in path:
        os.environ["PATH"] += os.pathsep + '/usr/bin'
        logging.debug("Added Path /usr/bin")

def installPkgs():
    osName = getDistributionName();
    output = "None"
    if "debain" in osName:
        output = execute("apt install -y libnginx-mod-http-lua", shell=True, stderr=subprocess.STDOUT)
    if "alpine" in osName:
        output = execute("apk add --no-cache nginx-mod-http-lua", shell=True, stderr=subprocess.STDOUT)

    if checkForErrorInOutput(output):
        logging.critical("error: installing pkg for %s platform" % osName)
    else:
        logging.info("success: installed pkg for %s platform" % osName)

def loadLdConfigEwaf(pathToAdd):
    # create the file and add the path
    filePath = os.path.join(pathToAdd, LD_CONF_FILE)
    removeLdConfigEwaf()
    confFilePath = os.path.join("/etc/ld.so.conf.d/", LD_CONF_FILE)
    with open(confFilePath, "w") as f:
       contents = pathToAdd
       f.write(contents)
       f.close()
       logging.info("success: update file at location %s" % confFilePath)

    # run ld config
    output = execute("ldconfig", shell=True, stderr=subprocess.STDOUT)
    if checkForErrorInOutput(output):
        logging.critical("error: executing ldconfig")
    else:
        logging.info("success: executed ldconfig")

def removeLdConfigEwaf():
    confFilePath = os.path.join("/etc/ld.so.conf.d/", LD_CONF_FILE)
    print("created filePath is %s" % confFilePath)
    if os.path.exists(confFilePath):
        os.remove(confFilePath)
        logging.debug("file %s already exists, removed the file" % confFilePath)
    logging.debug("skipped removing the file %s" % confFilePath)

def readFile(confLocation, encode = None):
    if os.path.isfile(confLocation) == False:
        return None
    try:
        if encode == None:
            with open(confLocation, "r") as f:
               contents = f.readlines()
               logging.info("success: read file at location %s" % confLocation)
               return contents
        else:
            with open(confLocation, "r", encoding=encode) as f:
               contents = f.readlines()
               logging.info("success: read file at location %s using encoding aryaman %s" % (confLocation, encode))
               return contents
    except EnvironmentError:
        err = "Error: reading " + confLocation
        return None

def writeFile(confLocation, contents, encode = None):
    # write back the updated contents
    success = False
    if encode == None:
        with open(confLocation, "w") as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
           logging.info("success: update file at location %s" % confLocation)
           success = True
    else:
        with open(confLocation, "w",  encoding=encode) as f:
           contents = "".join(contents)
           f.write(contents)
           f.close()
           logging.info("success: update file at location %s" % confLocation)
           success = True

    if success == False:
        logging.critical("Failed: error updating file at location %s" % confLocation)
  
def checkDeflate(restartCmd):
    logging.debug("Checking for deflate conf")
    restartCmd = restartCmd.lower()
    if "apache2" not in restartCmd:
        return False
    output = execute("apache2ctl -M | grep deflate_module" , shell=True, stderr=subprocess.STDOUT)
    #  output will be deflate_module (shared)
    if type(output) != str:
        output = output.decode()
    if "deflate_module" in output:
        return True
    return False

def insertStr(string, strToInsert, index):
    return string[:index] + strToInsert + string[index:]

def GetEnvironmentVariable(userName):
    try:
        env = subprocess.check_output(SWITCH_USER_CMD + userName + SUFFIX_CMD, stderr=subprocess.STDOUT, shell=True)
        return env
    except subprocess.CalledProcessError as error:
        logging.warning("Get env variable for user %s failed" % userName)
    return os.environ['PATH'].encode()

def GetPathVariable(userName):
    env = GetEnvironmentVariable(userName)
    contents = str(env, "utf-8").split("\n")
    for content in contents:
        if PATH in content:
            logging.debug("found path variable %s" % content)
            return content.replace(PATH, "", 1)
    return os.environ['PATH']

def findOwner(filename):
    return pwd.getpwuid(os.stat(filename).st_uid).pw_name

def findUid(filename):
    return os.stat(filename).st_uid

def findGid(filename):
    return os.stat(filename).st_gid

def isWritable(filename):
    return os.access(filename, os.W_OK)

def getCurrentUser():
    return pwd.getpwuid(os.getuid())[0]

def createBkp(orgLoc , bkpLoc):
    error = True
    try:
        shutil.copyfile(orgLoc, bkpLoc)
        logging.debug("Backup created successfully as %s" % bkpLoc)
        error = False
    # For other errors
    # If source and destination are same
    except shutil.SameFileError:
        logging.warning("Source and destination represents the same file.")
     
    # If there is any permission issue
    except PermissionError:
        logging.warning("Permission denied.")
    except:
        logging.warning("failed taking backup of files %s %s" %(orgLoc, bkpLoc))
    return error

def demote(userId, userGid, eduids=True):
    report_ids('starting demotion')
    if eduids:
        try:
            #os.setegid(userGid)
            os.setregid(userGid, userGid)
            os.setreuid(userId, userId)
        except:
            logging.warning('failed demotion')
            return
    else:
        try:
            #os.setgid(userGid)
            os.setuid(userId)
        except:
            logging.warning('failed demotion')
            return
    report_ids('finished demotion')

def report_ids(msg):
    logging.debug('uid %d, gid %d; and eduid %d, eguid %d %s' % (os.getuid(), os.getgid(),
                                                               os.getuid() , os.getegid(),
                                                               msg))

def executeCommand(command):
    logging.info("Executing command %s" % (command))
    try:
        output = subprocess.Popen(command,
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        rc = output.wait()
        stdout, stderr = output.communicate()
        logging.info(stdout)
        logging.debug(stderr)
        logging.debug(rc)
    except subprocess.CalledProcessError as error:
        stderr =  error.output
        rc = -1
        logging.warning("execute command %s failed" % output)
    return rc,stdout,stderr

def splitPath(path, count):
    if count <= 0:
        return path
    split = path
    for i in range(0, count):
        head, tail = os.path.split(split)
        split = head
    logging.debug("split path from %s is %s" % (path, split))
    return split