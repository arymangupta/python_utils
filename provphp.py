import sys
import subprocess
import os
import shutil
import re
import logging
import autoprov.ProcessUtil as ProcessUtil
import autoprov.autoprov as autoprov
import json

docRoot = webServer = phpVersion = phpConfigFolder = ""

PHP_IAE_DIR = "iae-php"
VSP_INI_FILE = "vsp.ini"
VSP_OPT_FOLDER = "/opt/virsec"

class Php:
    def __init__(self, *args): # pkgName, configDir, phpVersion):
        if (len(args) == 3):
            self.__pkgName = args[0]
            self.__configDir = args[1]
            self.__version = args[2]
            self.__zts = False

        if (len(args) == 1):
            self.__phpPath = args[0]
            self.__phpInfo = None
            self.InitPhpInfo()
            self.InitMetadata()

    def InitMetadata(self):
        self.__version = self.FindValue("^PHP Version => (.+)$")
        self.__configDir = self.FindValue('^Scan this dir for additional .ini files => (.+)$')
        self.__zts = self.FindValue('^Thread Safety => (.+)$') == "enabled"


    def InitPhpInfo(self):
        cmd = [self.__phpPath, "-d", "virseciae.disable=1", "-i"] 
        try:
            self.__phpInfo = ProcessUtil.execute(cmd, stderr=open(os.devnull, 'w+')).decode('latin-1')
        except subprocess.CalledProcessError as e:
             logging.debug("Error executing %s : %s" % (" ".join(cmd), e))

    def FindValue(self, regx, group=1):
        if not self.__phpInfo:
            return ""

        info = self.__phpInfo
        if info:
            matches = re.search(regx, info, flags=re.M)
            if matches:
                res = matches.group(group)
                if res != '(none)':
                    return res

        return ""

    def major(self):
        if self.__version:
            return int(self.__version.split('.')[0])

    def minor(self):
        if self.__version:
            return int(self.__version.split('.')[1])

    def patch(self):
        if self.__version:
            return int(self.__version.split('.')[2])

    def Version(self):
        if self.__version:
            return "%d.%d" % (self.major(), self.minor())
        else:
            return ""

    def ConfigFolder(self):
        return self.__configDir

    def IsZts(self):
        return self.__zts

class PhpDebianPackages:
    DebianPackageCmd = '/usr/bin/dpkg'
    DebianPackageQuery = '/usr/bin/dpkg-query'
    Packages = {
        'libapache2-mod-php5.6': {
            '_extension_dir': '/usr/lib/php/20131226',
            '_configuration_dir': '/etc/php/5.6/apache2/conf.d'
        },
        'libapache2-mod-php5': {
            '_extension_dir': '/usr/lib/php5/20131226',
            '_configuration_dir': '/etc/php5/apache2/conf.d'
        },
        'libapache2-mod-php7.0': {
            '_extension_dir': '/usr/lib/php/20151012',
            '_configuration_dir': '/etc/php/7.0/apache2/conf.d'
        },
        'libapache2-mod-php7.1': {
            '_extension_dir': '/usr/lib/php/20160303',
            '_configuration_dir': '/etc/php/7.1/apache2/conf.d'
        },
        'libapache2-mod-php7.2': {
            '_extension_dir': '/usr/lib/php/20170718',
            '_configuration_dir': '/etc/php/7.2/apache2/conf.d'
        },
        'libapache2-mod-php7.3': {
            '_extension_dir': '/usr/lib/php/20180731',
            '_configuration_dir': '/etc/php/7.3/apache2/conf.d'
        },
        'libapache2-mod-php7.4': {
            '_extension_dir': '/usr/lib/php/20190902',
            '_configuration_dir': '/etc/php/7.4/apache2/conf.d'
        },
        'libapache2-mod-php8.0': {
            '_extension_dir': '/usr/lib/php/20200930',
            '_configuration_dir': '/etc/php/8.0/apache2/conf.d'
        },
        'php5-cgi': {
            '_extension_dir': '/usr/lib/php5/20131226',
            '_configuration_dir': '/etc/php5/cgi/conf.d'
        },
        'php7.0-cgi': {
            '_extension_dir': '/usr/lib/php/20151012',
            '_configuration_dir': '/etc/php/7.0/cgi/conf.d'
        },
        'php7.1-cgi': {
            '_extension_dir': '/usr/lib/php/20160303',
            '_configuration_dir': '/etc/php/7.1/cgi/conf.d'
        },
        'php7.2-cgi': {
            '_extension_dir': '/usr/lib/php/20170718',
            '_configuration_dir': '/etc/php/7.2/cgi/conf.d'
        },
        'php7.3-cgi': {
            '_extension_dir': '/usr/lib/php/20180731',
            '_configuration_dir': '/etc/php/7.3/cgi/conf.d'
        },
        'php7.4-cgi': {
            '_extension_dir': '/usr/lib/php/20190902',
            '_configuration_dir': '/etc/php/7.4/cgi/conf.d'
        },
        'php8.0-cgi': {
            '_extension_dir': '/usr/lib/php/20200930',
            '_configuration_dir': '/etc/php/8.0/cgi/conf.d'
        },
    }

    def InstalledPackages(self):
        instldPackages = []

        if not os.path.exists(self.DebianPackageQuery):
            return instldPackages

        cmd = [self.DebianPackageQuery, '-W', '-f', '${binary:Package} ${Version}\n']
        try:
            outputs = ProcessUtil.execute(cmd, stderr=open(os.devnull, 'w+')).decode('latin-1').split("\n")

            #logging.debug("CMD - %s, Output: %s" % (cmd, outputs))

            outputs.pop()
            for line in outputs:
                items = line.split(" ")
                instldPackages.append([items[0], items[1].split('-')[0]])

        except subprocess.CalledProcessError as e:
            logging.debug("Command invocation error %s : %s" % (" ".join(cmd), e))

        return instldPackages

    def InstalledPhpPackages(self, reqVer):
        phpPckgs = []
        pckgs = self.InstalledPackages()
        for pckg in pckgs:
            if pckg[0] in self.Packages:
                fndPckg = self.Packages[pckg[0]]
                phpPckg = Php(pckg[0], fndPckg["_configuration_dir"], pckg[1])           
                if phpPckg.Version() == reqVer:
                    phpPckgs.append(phpPckg)
       
        return phpPckgs

class PhpKnownLocation:
    KnownFolders = [
        '/usr/php/bin',
        '/usr/php-7.0/bin',
        '/usr/php-7.1/bin',
        '/usr/php-7.2/bin',
        '/usr/php-7.3/bin',
        '/usr/php-7.4/bin',
        '/usr/php-8.0/bin',
        '/usr/php/7.0/bin',
        '/usr/php/7.1/bin',
        '/usr/php/7.2/bin',
        '/usr/php/7.3/bin',
        '/usr/php/7.4/bin',
        '/usr/php/8.0/bin',

        '/usr/local/bin',
        '/usr/local/php/bin',
        '/usr/local/zend/bin',
        '/usr/local/php-7.0/bin',
        '/usr/local/php-7.1/bin',
        '/usr/local/php-7.2/bin',
        '/usr/local/php-7.3/bin',
        '/usr/local/php-7.4/bin',
        '/usr/local/php-8.0/bin',

        '/opt/local/bin',
        '/opt/php/bin',
        '/opt/zend/bin',
        '/opt/php-7.0/bin',
        '/opt/php-7.1/bin',
        '/opt/php-7.2/bin',
        '/opt/php-7.3/bin',
        '/opt/php-7.4/bin',
        '/opt/php-8.0/bin',

        '/opt/cpanel/ea-php53/root/usr/bin',
        '/opt/cpanel/ea-php54/root/usr/bin',
        '/opt/cpanel/ea-php55/root/usr/bin',
        '/opt/cpanel/ea-php56/root/usr/bin',
        '/opt/cpanel/ea-php70/root/usr/bin',
        '/opt/cpanel/ea-php71/root/usr/bin',
        '/opt/cpanel/ea-php72/root/usr/bin',
        '/opt/cpanel/ea-php73/root/usr/bin',
        '/opt/cpanel/ea-php74/root/usr/bin',
        '/opt/cpanel/ea-php80/root/usr/bin',

        '/opt/cpanel/php/root/usr/bin',
        '/opt/cpanel/php/usr/bin',
        '/opt/cpanel/php/bin',

        '/RunCloud/Packages/php56rc/bin',
        '/RunCloud/Packages/php70rc/bin',
        '/RunCloud/Packages/php71rc/bin',
        '/RunCloud/Packages/php72rc/bin',
        '/RunCloud/Packages/php73rc/bin',
        '/RunCloud/Packages/php74rc/bin',
        '/RunCloud/Packages/php80rc/bin',

        '/opt/bitnami/php/bin',
        '/opt/bitnami/php-7.0/bin',
        '/opt/bitnami/php-7.1/bin',
        '/opt/bitnami/php-7.2/bin',
        '/opt/bitnami/php-7.3/bin',
        '/opt/bitnami/php-7.4/bin',
        '/opt/bitnami/php-8.0/bin',
        '/opt/bitnami/php/7.0/bin',
        '/opt/bitnami/php/7.1/bin',
        '/opt/bitnami/php/7.2/bin',
        '/opt/bitnami/php/7.3/bin',
        '/opt/bitnami/php/7.4/bin',
        '/opt/bitnami/php/8.0/bin',
    ]

    def InstalledPhps(self, reqVer):
        folders = os.environ.get('PATH', '').split(':') + self.__class__.KnownFolders
        folders = list(set(folders))
        insldPhp = []
        for fldr in folders:
            fndPhps = self.CheckPhp(fldr)
            if fndPhps:
                for foundPhp in fndPhps:
                    if foundPhp.Version() == reqVer:
                        insldPhp.append(foundPhp)

        return insldPhp

    def CheckPhp(self, fldr):
        phps = []
        if os.path.isdir(fldr):
            for name in os.listdir(fldr):
                if re.match('(zts-)?php([57])?(-fpm)?(-?\d(\.?\d+)?)?$', name):
                    file_path = os.path.join(fldr, name)
                    with open(file_path, 'rb') as fd:
                        if fd.read(4) != b"\x7fELF":
                            continue
                    phps.append(Php(file_path))

        return phps

def validateArgs(docRoot):
    if not os.path.isdir(docRoot):
        return False
    return True
    

def provPhp(action, docRoot, webServer, phpVersion, phpConfigFolder, appContextPath, refCount:int):
    status = validateArgs(docRoot)
    if status is False:
        error = "Doc %s root is not present" % docRoot
        logging.critical(error)
        return False

    logging.debug("PHP application - action %s docRoot %s,"
                 "webServer %s, phpVersion %s, phpConfigFolder %s, appContextPath %s,  refCount %s"
                  % (action, docRoot, webServer, phpVersion, phpConfigFolder, appContextPath, refCount))

# Action: Cleanup -> refcount is not ZERO
    if action == "clean":
        if refCount > 1:
            removeAppFiles(docRoot)
            return True

    vspIniFilePath = os.path.join(VSP_OPT_FOLDER, PHP_IAE_DIR, phpVersion, VSP_INI_FILE)
    if not os.path.isfile(vspIniFilePath):
        error = "File not found - %s" % vspIniFilePath
        logging.critical(error)
        return False

    knownPhps = PhpKnownLocation().InstalledPhps(phpVersion)
    instldPhpPackgs = PhpDebianPackages().InstalledPhpPackages(phpVersion)

    instldPhps = list()

    if (phpConfigFolder and not phpConfigFolder.isspace()):
        if os.path.isdir(phpConfigFolder):
            instldPhps.append(Php("custom", phpConfigFolder, phpVersion))
        else:
            error = "Configured PHP coniguration folder %s does not exist" % phpConfigFolder
            logging.critical(error)
            return False
    else:
        if (knownPhps):
            instldPhps.extend(knownPhps)
        if (instldPhpPackgs):
            instldPhps.extend(instldPhpPackgs)

    logging.debug("Installed packages - %d - %s" % (len(instldPhps), instldPhps))

    if len(instldPhps) == 0:
        error = "No Installed packages found check if php %s is installed" % phpVersion
        logging.warning(error)
        return False

    provisionedPhp = list()
    for ipcg in instldPhps:
        logging.debug("PHP Config folder %s" % (ipcg.ConfigFolder()))

        if ipcg.ConfigFolder() in provisionedPhp or ipcg.IsZts():
            continue

        targetIniPath = os.path.join(ipcg.ConfigFolder(), "vsp.ini")

        provisionedPhp.append(ipcg.ConfigFolder())

# Action: Provision
        if action == "prov":
            logging.debug("Copying file %s to %s" % (vspIniFilePath, targetIniPath))
            shutil.copyfile(vspIniFilePath, targetIniPath)
            os.chmod(targetIniPath, 0o644)
            virsecIae = os.path.join(docRoot, "VirsecIae.config")
            virsecResource = os.path.join(docRoot, "virsecresources.php")
            if(os.path.isfile(virsecIae)):
                os.remove(targetIniPath)
                logging.debug("file already present %s , removed %s " %( virsecIae, virsecIae))
            with open(os.path.join(docRoot, "VirsecIae.config"), 'w') as vcfg:
                dictionary:dict = dict()
                dictionary["LogPath"] = "/var/virsec/log"
                dictionary["LogLevel"] = "Info"
                dictionary["AppCtx"] = appContextPath
                json_object = json.dumps(dictionary, indent = 4)
                vcfg.write(json_object)
                logging.debug("saved file contents are %s " % json_object)
                os.chmod(os.path.join(docRoot, "VirsecIae.config"), 0o755)
                logging.debug("Success: created file %s" % virsecIae)
                vcfg.close()

            if(os.path.isfile(virsecResource)):
                os.remove(virsecResource)
                logging.debug("file already present %s , removed %s " %( virsecResource, virsecResource))
            with open(virsecResource, 'w') as vcfg:
                os.chmod(virsecResource, 0o755)
                logging.debug("Success: created file %s" % virsecResource)
                vcfg.close()
            ProcessUtil.selinuxLoadAndCompilePolicyModule(action)
            #ProcessUtil.restartPhp(webServer, phpVersion)

# Action: Cleanup -> refcount is 1 i.e last 
        elif action == "clean":
            if refCount <= 1:
                logging.debug("Trying to remove file %s" % targetIniPath)
                if os.path.isfile(targetIniPath):
                    os.remove(targetIniPath)
                    logging.debug("Success: removed file %s" % targetIniPath)
                else:
                    logging.debug("File not found %s" % targetIniPath)
                ProcessUtil.selinuxLoadAndCompilePolicyModule(action)
                #ProcessUtil.restartPhp(webServer, phpVersion)
            removeAppFiles(docRoot)
    return True

def removeAppFiles(docRoot):
    virsecIae = os.path.join(docRoot, "VirsecIae.config")
    virsecResource = os.path.join(docRoot, "virsecresources.php")
    if (os.path.isfile(virsecIae)):
        logging.debug("Removing file %s" % (os.path.join(docRoot, "VirsecIae.config")))
        os.remove(os.path.join(docRoot, "VirsecIae.config")) 
        logging.debug("Success: removed file %s" % virsecIae)
            
    if (os.path.isfile(virsecResource)):
        logging.debug("Removing file %s" % (os.path.join(docRoot, "virsecresources.php")))
        os.remove(os.path.join(docRoot, "virsecresources.php"))
        logging.debug("Success: removed file %s" % virsecResource)
