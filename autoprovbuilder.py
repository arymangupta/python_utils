import messages
from vsp_defines import VspKeys, VSPComponent , VSPInfo
import logging
from vsp_msg_enums import vmsg_enums
from autoprov.provjava import provJava
import autoprov.ProcessUtil as ProcessUtil
if ProcessUtil.getOsName().startswith('win'):
    from autoprov.provdotnet import provDotnet
from autoprov.provphp import provPhp, validateArgs
from autoprov.provserver import provNginx
from autoprov.provserver import provHttpd
from autoprov.provnodejs import provNodejs
from autoprov.provror import provRor

import subprocess
from cache import *
import os
import vsputils
import re

class BuildAutoprov:
    __message = None
    __processType: str = None

    def __init__(self, message):
        self.__message = message

    def Build(self):
        serviceType = self.__message.GetMsgDictValue(VspKeys.PD_KEY_SERVICE_TYPE)
        logging.info('serviceType is %s' % serviceType)
        if serviceType is not None:
            if serviceType == VspKeys.SERVICE_TYPE_APP:
                self.__processType = self.__message.GetMsgDictValue(VspKeys.PD_KEY_PROCESS_TYPE)
            elif serviceType == VspKeys.SERVICE_TYPE_WEB:
                self.__processType = self.__message.GetMsgDictValue(VspKeys.PD_KEY_WEB_SERVER_TYPE)
        if self.__processType is None:
            return None
        logging.debug('building autoprov builder of process type %s' % (self.__processType))
        if self.__processType == VspKeys.APPLICATION_JAVA:
            return JavaAutoprov(self.__message)
        if self.__processType == VspKeys.APPLICATION_PHP:
            return PhpAutoprov(self.__message)
        if self.__processType == VspKeys.APPLICATION_NODEJS:
            return NodeJsAutoprov(self.__message)
        if self.__processType == VspKeys.APPLICATION_RUBY:
            return RubyAutoprov(self.__message)
        if self.__processType == VspKeys.APPLICATION_DNET or self.__processType == VspKeys.APPLICATION_DNET_CORE:
            return DotNetAutoprov(self.__message)
        if self.__processType == VspKeys.SERVER_TYPE_NGINX:
            return NginxAutoprov(self.__message)
        if self.__processType == VspKeys.SERVER_TYPE_APACHE:
            return ApacheAutoprov(self.__message)
        logging.warning('unsuported process type %s' % self.__processType)


class AutoProv:
    message: messages.ProvisionMessage

    def __init__(self, message: messages.ProvisionMessage):
        self.message = message

    def GetAction(self):
        provFlag = 'true'
        action = 'prov'
        if self.message.GetAuxilaryFlags() & messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP:
            action = 'clean'
            provFlag = 'false'
            logging.debug('cleanup flag is set')
        return (action, provFlag)


class JavaAutoprov(AutoProv):
    _JavaAutoprov__processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        appContextPath = self.message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, '')
        serverType = self.message.metaDataDict.get(VspKeys.PD_KEY_SERVER_TYPE, '')
        startupScriptPath = self.message.metaDataDict.get(VspKeys.PD_KEY_CONFIG_FILE_PATH, '')
        serverName = self.message.metaDataDict.get(VspKeys.PD_KEY_SERVER_NAME, '')
        applicationType = self.message.metaDataDict.get(VspKeys.PD_KEY_APPTYPE, '')
        filterType = self.message.metaDataDict.get(VspKeys.PD_KEY_FILTERTYPE, '')
        instrumentationFilterClass = self.message.metaDataDict.get(VspKeys.PD_KEY_INSTRUMENTFILTERCLASS, '')
        filterMethod = self.message.metaDataDict.get(VspKeys.PD_KEY_FILTERMETHOD, '')
        filterPosition = self.message.metaDataDict.get(VspKeys.PD_KEY_FILTERPOSITION, '')
        action, ignore = self.GetAction()
        return provJava(action, serverType,
                        startupScriptPath,
                        appContextPath,
                        serverName,
                        applicationType,
                        filterType,
                        instrumentationFilterClass,
                        filterMethod,
                        filterPosition)


class PhpAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        applicationDepFolder = self.message.msgDict.get(VspKeys.PD_KEY_APP_PATH, [])[0]
        serverType = self.message.metaDataDict.get(VspKeys.PD_KEY_SERVER_TYPE, '')
        phpVersion = self.message.metaDataDict.get(VspKeys.PD_KEY_VERSION, '')
        phpConfigFolder = None
        appContextPath = self.message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, '')
        action, ignore = self.GetAction()
        refCount = RefCountCache().GetCount(phpVersion)
        success = provPhp(action,
                          applicationDepFolder,
                          serverType,
                          phpVersion,
                          phpConfigFolder,
                          appContextPath,
                          refCount)
        if success is True:
            if action == 'prov':
                RefCountCache().Incr(phpVersion)
        if (action == 'clean' and not self.message.GetAuxilaryFlags()
           & messages.AuxilaryInfo.AUX_FLAG_SKIP_REFCOUNT_CHANGE):
            RefCountCache().Decr(phpVersion)
        return success


class NodeJsAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def __Validate(self, version:str):
        if re.search('[a-zA-Z]', version) is True:
            logging.warning("invalid version %s" % version)
            return False
        start = vsputils.Versiontuple("8.17.0")
        curr = vsputils.Versiontuple(version)
        end = vsputils.Versiontuple("14.0.0")
        if curr >= start and curr <= end:
            return True
        logging.critical("version not supproted %s" % version)
        return False

    def Autoprov(self):
        applicationDepFolder = self.message.msgDict.get(VspKeys.PD_KEY_APP_PATH, [])[0]
        nodeJsVersion = self.message.metaDataDict.get(VspKeys.PD_KEY_VERSION, None)
        appConfigFilePath = self.message.metaDataDict.get(VspKeys.PD_KEY_CONFIG_FILE_PATH, None)
        appContextPath = self.message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
        action, ignore = self.GetAction()
        if self.__Validate(nodeJsVersion) is False:
            return False
        status = False
        try:
            status = provNodejs(action, applicationDepFolder, appConfigFilePath,
                         appContextPath, nodeJsVersion)
        except:
            logging.warning("exception raise")
        return status


class DotNetAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        applicationType = self.message.msgDict.get(VspKeys.PD_KEY_PROCESS_TYPE, '')
        applicationContext = self.message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, '')
        applicationDepFolder = self.message.msgDict.get(VspKeys.PD_KEY_APP_PATH, [])[0]
        ignore, provisionFlag = self.GetAction()
        return provDotnet(applicationType,
                          applicationContext,
                          applicationDepFolder,
                          provisionFlag)


class RubyAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        output = ""
        applicationDepFolder = self.message.msgDict.get(VspKeys.PD_KEY_APP_PATH, [])[0]
        scriptPath = os.path.join(VSPInfo.VSP_BIN_HOME, "iae-ruby", "scripts")
        action, ignore = self.GetAction()
        applicationContext = self.message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
        status = False

        try:
           status = provRor(action, applicationDepFolder,
                  applicationContext)
        except:
            logging.critical("Exception riased")
            status =  False
        if status is False:
            if action == 'prov':
                scriptPath = os.path.join(scriptPath, "provisionRor.sh")
            elif action == 'clean':
                scriptPath = os.path.join(scriptPath, "unProvisionRor.sh")
            
            if not os.path.isfile(scriptPath):
                logging.critical("script path %s is not present" % scriptPath)
                return False
            try:
                #cmd = "f{scriptPath} f{applicationDepFolder} f{applicationContext}"
                output = subprocess.run([scriptPath,
                                        applicationDepFolder,
                                        applicationContext],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as error:
                output =  error.output
                status =  False
            logging.info("ruby script execution output %s" % output)
            status =  not ProcessUtil.checkForErrorInOutput(str(output))
        return status


class ApacheAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        serverName = self.message.msgDict.get(VspKeys.PD_KEY_SERVER_NAME, '')
        confLocation = "find"
        restartCommand = self.message.msgDict.get(VspKeys.PD_KEY_WEB_SERVER_CMD, '')
        arg0 = str("'LoadFile /opt/virsec/lib/libiae_encode.so'")
        arg1 = str("'LoadFile /opt/virsec/lib/libIAE-Assist.so'")
        arg2 = str("'LoadModule vs_req_module /opt/virsec/ewaf/apache/mod_vs_req.so'")
        arg3 = str("'LoadModule vs_resp_module /opt/virsec/ewaf/apache/mod_vs_resp.so'")
        action, ignore = self.GetAction()
        return provHttpd(action,
                         confLocation,
                         restartCommand,
                         arg0, arg1, arg2, arg3)


class NginxAutoprov(AutoProv):
    __processType: str

    def __init__(self, message):
        super().__init__(message)

    def Autoprov(self):
        serverName = self.message.msgDict.get(VspKeys.PD_KEY_SERVER_NAME, '')
        confLocation = "find"
        serverBlock = "http"
        restartCommand = self.message.msgDict.get(VspKeys.PD_KEY_WEB_SERVER_CMD, '')
        arg0 = str(" 1 'lua_package_path:\"/opt/virsec/ewaf/nginx/?.lua;;\"'")
        arg1 = str(" 2 'lua_package_cpath:\"/opt/virsec/ewaf/nginx/?.so;;\"'")
        arg2 = str(" 3 'lua_need_request_body:on'")
        arg3 = str(" 6 'access_by_lua_file:/opt/virsec/ewaf/nginx/vs_req_filter.lua'")
        arg4 = str(" 7 'body_filter_by_lua_file:/opt/virsec/ewaf/nginx/vs_resp_filter.lua'")
        action, ignore = self.GetAction()

        return provNginx(action,
                         confLocation,
                         restartCommand,
                         serverBlock,
                         arg0, arg1, arg2, arg3, arg4)



def test():
    provNginx('prov', 'find', 'systemctl restart nginx' ,'http', ' 1 \'lua_package_path:"/opt/virsec/ewaf/nginx/?.lua;;"\'',
                                                     ' 2 \'lua_package_cpath:"/opt/virsec/ewaf/nginx/?.so;;"\'',
                                                    " 3 'lua_need_request_body:on'",
                                                    " 4 'client_body_buffer_size:128k'", " 5 'client_max_body_size:100M'",
                                                   " 6 'access_by_lua_file:/opt/virsec/ewaf/nginx/vs_req_filter.lua'",
                                                   " 7 'body_filter_by_lua_file:/opt/virsec/ewaf/nginx/vs_resp_filter.lua'")
#test()