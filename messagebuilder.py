import json, messages, logging
from vsp_msg_enums import vmsg_enums, CONFIG_MSG_TYPE, PROV_START_JOB, vmsg_types
from vsp_defines import VSPInfo, VSPComponent, VspKeys, VspVulMask
import os

class FactoryMessageBuilder:
    """ Builds Message Builder based on the message type"""
    __messageType = -1
    __messageType: int
    __jsonDict = {}
    __jsonDict: dict

    def __init__(self, jsonDict=None, jsonMsg: str=None, filePath: str=None):
        if filePath is not None:
            with open(filePath) as (f):
                try:
                    self.__jsonDict = json.load(f)
                except json.JSONDecodeError as err_msg:
                    try:
                        logging.error('{} is a malformed json; error msg: {}'.format(filePath, err_msg))
                    finally:
                        err_msg = None
                        del err_msg

        elif jsonMsg is not None:
            self.__jsonDict = json.loads(jsonMsg)

        elif jsonDict is not None:
            self.__jsonDict = jsonDict

        self.__setJsonMsgType()

    def __setJsonMsgType(self):
        self.__messageType = self.__jsonDict[VspKeys.PD_KEY_MSG_TYPE]

    def BuildMessageBuilder(self):
        logging.info('building message type %d', self.__messageType)
        component = VSPComponent.vweb_assist
        if self.__messageType is vmsg_types[VSPComponent.vweb_assist].get('CONFIG', 1):
            return ConfigMessageBuilder(self.__jsonDict)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROCESS_CONTROL', 2):
            return ProcessControlMessageBuilder(self.__jsonDict)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROV_START_JOB', 6):
            return ProvisionMessageBuilder(self.__jsonDict)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROV_STOP_JOB', 7):
            return UnprovisionMessageBuilder(self.__jsonDict)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('INTERNAL_STATE', 5):
            return InternalStateMessageBuilder(self.__jsonDict)
        logging.warning('unsuported message type %d', self.__messageType)
        return None


class CommonMessageBuilder:
    """ Build common message """

    def BuildCommon(self, msgDict: dict, message: messages.Message):
        message.commonHdrMsgDict[VspKeys.PD_KEY_VERSION] = msgDict.get(VspKeys.PD_KEY_VERSION, '0')
        message.commonHdrMsgDict[VspKeys.PD_KEY_TARGET_VSP_COMP] = msgDict.get(VspKeys.PD_KEY_TARGET_VSP_COMP, None)
        message.commonHdrMsgDict[VspKeys.PD_KEY_SOURCE_VSP_COMP] = msgDict.get(VspKeys.PD_KEY_SOURCE_VSP_COMP, None)
        message.commonHdrMsgDict[VspKeys.PD_KEY_MSG_TYPE] = msgDict.get(VspKeys.PD_KEY_MSG_TYPE, 0)
        message.commonHdrMsgDict[VspKeys.PD_KEY_MSG_TXNID] = msgDict.get(VspKeys.PD_KEY_MSG_TXNID, None)
        message.commonHdrMsgDict[VspKeys.PD_KEY_FEEDBACK_REQ] = msgDict.get(VspKeys.PD_KEY_FEEDBACK_REQ, 0)
        message.commonHdrMsgDict[VspKeys.PD_KEY_DEPLOYMENT_TYPE] = msgDict.get(VspKeys.PD_KEY_DEPLOYMENT_TYPE, None)
        message.commonHdrMsgDict[VspKeys.PD_KEY_ASI_ID] = msgDict.get(VspKeys.PD_KEY_ASI_ID, None)


class ConfigMessageBuilder(CommonMessageBuilder):
    """ Build Config Message """
    __jsonDict:dict
    __message:messages.ConfigMessage

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        if self.__jsonDict.get(VspKeys.PD_KEY_CONFIGS, False) is not False:
            return True
        return False

    def BuildMessage(self):
        """
        Parsing logic
        """
        msgList = []
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        self.__PopulateConfigMessage()
        logging.info('Built config message %s' % self.__message)
        msgList.append(self.__message)
        return msgList

    def __PopulateConfigMessage(self):
        """ Populate config message """
        self.__message = messages.ConfigMessage(self.__jsonDict)

        messages.Message().commonHdrMsgDict
        self.BuildCommon(self.__jsonDict, self.__message)
        d = self.__jsonDict.get(VspKeys.PD_KEY_CONFIGS)
        if d is None:
            return

        # log level
        self.__message.msgDict[VspKeys.CFG_LOG_LEVEL] = d.pop(
            VspKeys.CFG_LOG_LEVEL, 'INFO')

        # log path
        self.__message.msgDict[VspKeys.CFG_LOG_PATH] = d.pop(
            VspKeys.CFG_LOG_PATH, os.path.join(VSPInfo.VSP_LOGS, 'web-assist'))
        
        if not os.path.isabs(self.__message.msgDict[VspKeys.CFG_LOG_PATH]):
            self.__message.msgDict[VspKeys.CFG_LOG_PATH] = os.path.join(
                VSPInfo.VSP_LOGS, self.__message.msgDict[VspKeys.CFG_LOG_PATH])
        self.__message.msgDict[VspKeys.CFG_LOG_PATH] = os.path.join(
            self.__message.msgDict[VspKeys.CFG_LOG_PATH], 'web-assist.log')
        
        self.__message.msgDict[VspKeys.CFG_LOG_MAX_FILE_SIZE] = d.pop(
            VspKeys.CFG_LOG_MAX_FILE_SIZE, 5000000)
        
        self.__message.msgDict[VspKeys.CFG_LOG_ROTATE_COUNT] = d.pop(
            VspKeys.CFG_LOG_ROTATE_COUNT, 20)
        
        self.__message.msgDict[VspKeys.CFG_STATS_PATH] = d.pop(
            VspKeys.CFG_STATS_PATH, 'web-assist')
        self.__message.msgDict[VspKeys.CFG_STATS_REFRESH_RATE] = d.pop(
            VspKeys.CFG_STATS_REFRESH_RATE, 10000)
        
        if self.__message.msgDict[VspKeys.CFG_STATS_REFRESH_RATE] <= 0:
            self.__message.msgDict[VspKeys.CFG_STATS_REFRESH_RATE] = 3000
        self.__message.msgDict[VspKeys.CFG_STATS_ROOT_DIR] = os.environ.get(
            'VSP_VSPSTATS_ENV', None)
        
        if (self.__message.msgDict[VspKeys.CFG_STATS_ROOT_DIR] or VSPInfo.PLATFORM) == 'LINUX':
            self.__message.msgDict[VspKeys.CFG_STATS_ROOT_DIR] = '/vspstats'
        else:
            if VSPInfo.PLATFORM == 'WINDOWS':
                self.__message.msgDict[VspKeys.CFG_STATS_ROOT_DIR] = os.path.join(
                    VSPInfo.VSP_BIN_HOME, 'vsp_stats')
        
        # vipc init max retry
        key = VspKeys.CFG_VIPC_INIT_RETRY
        self.__message.msgDict[key] = d.pop(key, 10)
        if self.__message.msgDict[key] <= 0:
            self.__message.msgDict[key] = 10
        
        # vipc init retry timeout
        key = VspKeys.CFG_VIPC_INIT_RETRY_TIMEOUT
        self.__message.msgDict[key] = d.pop(key, 3000)
        if self.__message.msgDict[key] <= 0:
            self.__message.msgDict[key] = 3000
        self.__message.msgDict[VspKeys.CFG_HB_FREQ] = d.pop(
            VspKeys.CFG_HB_FREQ, 2500)
        
        # hb freq
        if self.__message.msgDict[VspKeys.CFG_HB_FREQ] <= 0:
            self.__message.msgDict[VspKeys.CFG_HB_FREQ] = 2500
        
        if VSPInfo.PLATFORM == 'LINUX':
            vIPC_lib = 'libIAE-Assist.so'
        else:
            if VSPInfo.PLATFORM == 'WINDOWS':
                vIPC_lib = 'IAE-Assist.dll'
        
        # vipc lib path
        self.__message.msgDict[VspKeys.CFG_VIPC_LIB_PATH] = d.pop('vIPCLibPath', os.path.join(
            VSPInfo.VSP_LIB_DIR, vIPC_lib))
        if not os.path.isabs(self.__message.msgDict[VspKeys.CFG_VIPC_LIB_PATH]):
            self.__message.msgDict[VspKeys.CFG_VIPC_LIB_PATH] = os.path.join(
                VSPInfo.VSP_BIN_HOME, self.__message.msgDict[VspKeys.CFG_VIPC_LIB_PATH])
        
        if not os.path.exists(self.__message.msgDict[VspKeys.CFG_VIPC_LIB_PATH]):
            logging.error('For config vIPCLibPath, {} does not exist'.format(self.__message.msgDict[
                VspKeys.CFG_VIPC_LIB_PATH]))
        
        # vipc msg size
        self.__message.msgDict[VspKeys.CFG_VIPC_MAX_MSG_SIZE] = d.pop(
            VspKeys.CFG_VIPC_MAX_MSG_SIZE, 16384)
        
         # vipc read timeout
        self.__message.msgDict[VspKeys.CFG_VIPC_READ_TIMEOUT] = d.pop(
            VspKeys.CFG_VIPC_READ_TIMEOUT, 3000)
        
         # vsp msg enum path
        self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH] = d.pop(
            VspKeys.CFG_VSP_MSG_ENUM_PATH, os.path.join(
            VSPInfo.VSP_CONFIG_DIR, 'vsp_msg_type_enums.json'))
        
        if not os.path.isabs(self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH]):
            self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH] = os.path.join(
                VSPInfo.VSP_BIN_HOME, self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH])
        
        os.path.exists(self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH]) or logging.error(
            'For config vspMsgTypesEnumsPath, {} does not exist'.format(
            self.__message.msgDict[VspKeys.CFG_VSP_MSG_ENUM_PATH]))
        
        # iae-agents log level
        key = VspKeys.CFG_LANG_UPDATE_LOG_LEVEL
        self.__message.msgDict[key] = d.pop(key, None)
        
        # iae-agents log path
        key = VspKeys.CFG_LANG_UPDATE_LOG_PATH
        self.__message.msgDict[key] = d.pop(key, None)


class ProvisionMessageBuilder(CommonMessageBuilder):
    """ Build Provision Message """
    __jsonDict: dict

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        return True

    def BuildMessage(self):
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        msgList = []
        parentDict = self.__jsonDict
        nameSpace = parentDict.get(VspKeys.PD_KEY_NAMESPACE, None)
        nameSpaceDict = parentDict.get(str(nameSpace) , {})
        for appCollectiveId in nameSpaceDict:
            collectiveDict = nameSpaceDict[appCollectiveId]
            logging.info('namespace is %s' % nameSpace)
            message = messages.ProvisionMessage(self.__jsonDict)
            message.SetMsgDict(collectiveDict)
            # TODO:- Revmove, there some issue on vsp-cli stop of web-assist for this this is being done
            message.msgDict[VspKeys.PD_KEY_MSG_TYPE] = message.msgDict.get(VspKeys.PD_KEY_MSG_TYPE, 0)
            # set namespace
            message.msgDict[VspKeys.PD_KEY_NAMESPACE] = nameSpace
            # set request Id
            message.msgDict[VspKeys.PD_KEY_REQUEST_ID] = parentDict.get(VspKeys.PD_KEY_REQUEST_ID, -1)
            # set autoprov flag
            message.msgDict[VspKeys.PD_KEY_AUTOPROV_FLAG] = collectiveDict.get(
                VspKeys.PD_KEY_AUTOPROV_FLAG, True)
            # set app collective Id
            message.msgDict[VspKeys.PD_KEY_APP_COLLECTIVE_ID] = appCollectiveId
            # Build common
            self.BuildCommon(self.__jsonDict, message)
            # populate message
            self.__Populate(message, collectiveDict, parentDict, appCollectiveId)
            logging.debug('built message %s' % message.iaePbConfig)
            msgList.append(message)
        return msgList

    def __Populate(self, message: messages.ProvisionMessage, collectiveDict: dict,
                   parentDict: dict, appCollectiveId):
        serviceType = collectiveDict.get(VspKeys.PD_KEY_SERVICE_TYPE, None)
        if serviceType == VspKeys.SERVICE_TYPE_WEB:
            self.__PopulateIaeWebCollective(message, collectiveDict)
            # set the context path
            # Note: for web service the app context is server type
            message.msgDict[VspKeys.PD_KEY_CONTEXT_PATH] = collectiveDict.get(VspKeys.PD_KEY_WEB_SERVER_TYPE, None)
            logging.debug("setting app context as %s for web service" % message.msgDict[VspKeys.PD_KEY_CONTEXT_PATH])
        elif serviceType == VspKeys.SERVICE_TYPE_APP:
            self.__PopulateIaeAppCollective(message, collectiveDict)
            self.__PopulateIaeMetaData(message, collectiveDict)
            self.__PopulateLfiRfi(message, collectiveDict)
        else:
            logging.warning("unknown service type found %s" % serviceType or "None")
            return
        message.msgDict[VspKeys.SERVICE_TYPE_WEB] = serviceType
        self.__PopulateCommon(message, collectiveDict, parentDict, appCollectiveId)

    def __PopulateCommon(self, message: messages.ProvisionMessage, collectiveDict: dict,
                         parentDict: dict, appCollectiveId):
        common = message.iaePbConfig.common
        common.asiId = parentDict[VspKeys.PD_KEY_ASI_ID]
        common.namespaceId = int(parentDict[VspKeys.PD_KEY_NAMESPACE])
        common.appCollectiveId = int(appCollectiveId)
        common.runningMapVersion = int(0)
        self.__PopulateVulInfo(message, collectiveDict)

    def __PopulateIaeWebCollective(self, message: messages.ProvisionMessage, collectiveDict: dict):
        message.iaePbConfig.configType = message.iaePbConfig.WEB_COLLECTIVE
        webCollectiveConfig = message.iaePbConfig.webCollectiveConfig
        webCollectiveConfig.webServerName = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_NAME]
        webCollectiveConfig.webServerType = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_TYPE]
        webCollectiveConfig.webServerCMD = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_CMD]
        webCollectiveConfig.webServerCfg = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_CFG_PATH]
        webCollectiveConfig.webServerVersion = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_VERSION]
        webCollectiveConfig.webServerLogPath = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_LOG_PATH]
        webCollectiveConfig.webServerBinPath = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_BIN_PATH]
        message.msgDict[VspKeys.PD_KEY_WEB_SERVER_CMD] = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_CFG_PATH]
        hostNames = collectiveDict[VspKeys.PD_KEY_WEB_SERVER_APP_HOST_NAME]
        for name in hostNames:
            webCollectiveConfig.applicationHostName.extend(name)
        else:
            logging.debug('populated web collective config %s' % webCollectiveConfig)

    def __PopulateIaeAppCollective(self, message: messages.ProvisionMessage, collectiveDict: dict):
        message.iaePbConfig.configType = message.iaePbConfig.APP_COLLECTIVE
        appCollectiveConfig = message.iaePbConfig.appCollectiveConfig
        appCollectiveConfig.appName = collectiveDict[VspKeys.PD_KEY_APP_NAME]
        appPaths = collectiveDict[VspKeys.PD_KEY_APP_PATH]
        appCollectiveConfig.appPath.extend(appPaths)
        appCollectiveConfig.appName = collectiveDict[VspKeys.PD_KEY_APP_NAME]
        logging.debug('populated app collective config %s' % appCollectiveConfig)

    def __PopulateIaeMetaData(self, message: messages.ProvisionMessage, collectiveDict: dict):
        if collectiveDict.get(VspKeys.PD_KEY_METADATA, False) is False:
            logging.warn('metadata is missing')
            return None
        metaDataDict = collectiveDict[VspKeys.PD_KEY_METADATA]
        message.metaDataDict = metaDataDict
        # set the context path
        # Note: for web service the app context is server type
        message.msgDict[VspKeys.PD_KEY_CONTEXT_PATH] = message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
        logging.debug("setting app context as %s for app service" % message.msgDict[VspKeys.PD_KEY_CONTEXT_PATH])
        logging.debug('populated metadata %s' % metaDataDict)
        logging.debug('populated provision dicitionay %s' % message.msgDict)

    def __PopulateLfiRfi(self, message: messages.ProvisionMessage, collectiveDict: dict):
        data = collectiveDict.get(VspKeys.PD_KEY_LFI_DIRECTORIES, None)
        if data is None:
            logging.debug('lfi directories are missing')
        else:
            lfi = message.iaePbConfig.appCollectiveConfig.LfiMap
            directories = str(data).split(',')
            lfi.dirs.extend(directories)
        data = collectiveDict.get(VspKeys.PD_KEY_LFI_EXTENSIONS, None)
        if data is None:
            logging.debug('lfi extentions are missing')
        else:
            lfi = message.iaePbConfig.appCollectiveConfig.LfiMap
            extentions = str(data).split(',')
            lfi.exts.extend(extentions)
        data = collectiveDict.get(VspKeys.PD_KEY_RFI_URLS, None)
        if data is None:
            logging.debug('rfi urls are missing')
        else:
            rfi = message.iaePbConfig.appCollectiveConfig.RfiMap
            extentions = str(data).split(',')
            rfi.urls.extend(extentions)

    def __PopulateVulInfo(self, message: messages.ProvisionMessage, collectiveDict: dict):
        common = message.iaePbConfig.common
        vulMask = 0
        protectVulMask = 0
        
        # BE
        protectModeType = common.BE = collectiveDict.get(
            VspKeys.PD_KEY_BE, common.NONE - 1) + 1
        vulMaskValue = 0
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # CMDI
        protectModeType = common.CMDi = collectiveDict.get(
            VspKeys.PD_KEY_CMDI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.CMDI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # CSRF
        protectModeType = common.CSRF = collectiveDict.get(
            VspKeys.PD_KEY_CSRF, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.CSRF_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Custom
        protectModeType = common.custom = collectiveDict.get(
            VspKeys.PD_KEY_CUSTOM, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.CUSTOM_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Method Enforcement
        protectModeType = common.methodEnforcement = collectiveDict.get(
            VspKeys.PD_KEY_METHOD_ENFORCE, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.PROTO_ENFORCE_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Path Traversal
        protectModeType = common.pathTraversali = collectiveDict.get(
            VspKeys.PD_KEY_PT, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.PATH_TRAVERSALI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Reflective XSS
        protectModeType = common.reflectiveXSS = collectiveDict.get(
            VspKeys.PD_KEY_RXSS, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.REFLECTIVE_XSS_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Protocol Attack
        protectModeType = common.protocolAttack = collectiveDict.get(
            VspKeys.PD_KEY_PROTO_ATTACK, common.NONE - 1) + 1
        vulMaskValue = 0
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Protocol Enforcement
        protectModeType = common.protocolEnforcement = collectiveDict.get(
            VspKeys.PD_KEY_PROTO_ENFORCE, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.PROTO_ENFORCE_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # Stored XSS
        protectModeType = common.storedXSS = collectiveDict.get(
            VspKeys.PD_KEY_SXSS, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.STORED_XSS_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # DOM XSS, only detect with no vul mask
        protectModeType = collectiveDict.get(
           VspKeys.PD_KEY_DOMXSS, common.NONE - 1) + 1
        if protectModeType is not common.NONE:
            common.domXSS = common.DETECT
        if protectModeType is common.NONE:
            common.domXSS = protectModeType

        # SW Exception, only detect
        protectModeType = collectiveDict.get(
            VspKeys.PD_KEY_SW_EXCE_LOG,common.NONE - 1) + 1
        vulMaskValue = VspVulMask.SW_EXCEPTION_VULNERABILITY_MASK
        if protectModeType is not common.NONE:
            common.softwareExcLog = common.DETECT
            vulMask += vulMaskValue
        if protectModeType is common.NONE:
             common.softwareExcLog = protectModeType

        # Class Load, only detect
        protectModeType = collectiveDict.get(
            VspKeys.PD_KEY_CLASS_LOAD_LOG, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.CLASS_LOAD_VULNERABILITY_MASK
        if protectModeType is not common.NONE:
            common.classLoadLog = common.DETECT
            vulMask += vulMaskValue
        if protectModeType is common.NONE:
            common.classLoadLog = protectModeType

        # SQL Log
        protectModeType = common.urlSQLLog = collectiveDict.get(
            VspKeys.PD_KEY_URL_SQLLOG, common.NONE - 1) + 1
        vulMaskValue = 0
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # RFI
        protectModeType = common.RFI = collectiveDict.get(
            VspKeys.PD_KEY_RFI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.RFI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # LFI
        protectModeType = common.LFI = collectiveDict.get(
            VspKeys.PD_KEY_LFI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.LFI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # SQLI
        protectModeType = common.SQLi = collectiveDict.get(
            VspKeys.PD_KEY_SQLI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.SQLI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # CRLFi
        protectModeType = common.CRLFi = collectiveDict.get(
            VspKeys.PD_KEY_CRLFI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.CRLFI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        # XMLI
        protectModeType = common.XMLInjection = collectiveDict.get(
            VspKeys.PD_KEY_XMLI, common.NONE - 1) + 1
        vulMaskValue = VspVulMask.XMLI_VULNERABILITY_MASK
        if protectModeType is common.PROTECT:
            protectVulMask += vulMaskValue
        if protectModeType is not common.NONE:
            vulMask += vulMaskValue

        if collectiveDict.get(VspKeys.PD_KEY_INLINE_PROTECTION_MODE, False):
            common.protectMode = collectiveDict[VspKeys.PD_KEY_INLINE_PROTECTION_MODE]
        common.vulMask = vulMask
        common.protectVulMask = protectVulMask


class UnprovisionMessageBuilder(CommonMessageBuilder):
    __jsonDict: dict
    __msgList = list()

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        return True

    def BuildMessage(self):
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        message = messages.UnprovisionMessage(self.__jsonDict)
        self.BuildCommon(self.__jsonDict, message)
        key = VspKeys.PD_KEY_NAMESPACE
        message.msgDict[key] = self.__jsonDict.get(key, None)
        self.__msgList.append(message)
        logging.info('size %d' % len(self.__msgList))
        return self.__msgList


class ProcessControlMessageBuilder(CommonMessageBuilder):
    __jsonDict: dict
    __msgList = list()

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        return True

    def BuildMessage(self):
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        message = messages.ProcessControlMessage(self.__jsonDict)
        self.BuildCommon(self.__jsonDict, message)
        self.__msgList.append(message)
        return self.__msgList

class InternalStateMessageBuilder(CommonMessageBuilder):
    __jsonDict: dict
    __msgList = list()

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        return True

    def BuildMessage(self):
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        message = messages.ProcessControlMessage(self.__jsonDict)
        self.BuildCommon(self.__jsonDict, message)
        self.PopulateMsg(message)
        self.__msgList.append(message)
        return self.__msgList
    
    def PopulateMsg(self , message:messages.InternalStateMessage):
        message.msgDict[VspKeys.PD_KEY_FINAL_PROV_STATUS] = self.__jsonDict.pop(
            VspKeys.PD_KEY_FINAL_PROV_STATUS, None)
        message.msgDict[VspKeys.PD_KEY_SEGMENTED_RESPONSE] = self.__jsonDict.pop(
            VspKeys.PD_KEY_SEGMENTED_RESPONSE, None)
        message.msgDict[VspKeys.CFG_STATE_ID] = self.__jsonDict.pop(
            VspKeys.CFG_STATE_ID, None)
        message.msgDict[VspKeys.CFG_SUBSTATES] = self.__jsonDict.pop(
            VspKeys.CFG_SUBSTATES, None)

class FilePurgeMessageBuilder(CommonMessageBuilder):
    __jsonDict: dict
    __msgList = list()

    def __init__(self, jsonDict: dict):
        self.__jsonDict = jsonDict

    def __ValidateDict(self):
        return True

    def BuildMessage(self):
        if self.__ValidateDict() is not True:
            logging.info('Failed validate check')
            return list()
        message = messages.FilePurgeMessage(self.__jsonDict)
        self.BuildCommon(self.__jsonDict, message)
        # currently only supproted for php
        message.msgDict[VspKeys.PD_KEY_PROCESS_TYPE] = VspKeys.APPLICATION_PHP
        self.__msgList.append(message)
        return self.__msgList
        