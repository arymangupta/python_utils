from email import message
import messages, vsp_msg_enums
from vsp_defines import VSPInfo, VspKeys, VSPComponent
import logging, os
from vsplogger import LogCollector
from vsp_stats import VSPStats
from cache import *
from autoprov.provconfig import updateConfFile
from vsp_msg_enums import vmsg_enums, CONFIG_MSG_TYPE, PROV_START_JOB, vmsg_types
import autoprovbuilder
from loadlibrary import IaeAssistLibrary
import vsputils
import json
from googleproto.IAE_Configs_pb2 import *
import time
import shutil

class BuildMessageProcessor:
    __message: messages.Message
    __messageType: int

    def __init__(self, message):
        self.__message = message

    def Build(self):
        self.__messageType = self.__message.Get(VspKeys.PD_KEY_MSG_TYPE)
        logging.debug('Trying building message processor of type %d' % self.__messageType)
        if self.__messageType is vmsg_types[VSPComponent.vweb_assist].get('CONFIG', 1):
            return ConfigMessageProcessor(self.__message)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROCESS_CONTROL', 2):
            return ProcessControlMessageProcessor(self.__message)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROV_START_JOB', 6):
            return ProvisionMessageProcessor(self.__message)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('PROV_STOP_JOB', 7):
            return UnprovisionMessageProcessor(self.__message)
        if self.__messageType is vmsg_enums[VSPComponent.vweb_assist].get('INTERNAL_STATE', 5):
            return InternalStateMessageProcessor(self.__message)     
        logging.warning('unsuported message type %d', self.messageType)

class ConfigMessageProcessor(messages.Error):
    __message = None
    __message: messages.ConfigMessage

    def __init__(self, message: messages.ConfigMessage):
        self.__message = message

    def __Validate(self):
        return True

    def ProcessMessage(self):
        if self.__Validate() is not True:
            logging.info('Failed validate check')
            return False

        logging.debug('ConfigMessageProcessor processing message')
        auxFlags = self.__message.GetAuxilaryFlags()
        if auxFlags & messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP:
            logging.debug('skipped processing, cleanup flag is set')
            return None
        messageType = self.__message.Get(VspKeys.PD_KEY_MSG_TYPE)
        if messageType is None or messageType is not vsp_msg_enums.CONFIG_MSG_TYPE:
            return False
        self.__UpdateLoggingParms()
        self.__UpdateStatsParams()
        self.__UpdateIaeAgentsConfigFiles()
        return True

    def __UpdateLoggingParms(self):
        msgDict = self.__message.msgDict
        logCollectotInstance = LogCollector()
        logLevel = msgDict.get(VspKeys.CFG_LOG_LEVEL)
        logCollectotInstance.SetLogLevel(logLevel)
        logPath = msgDict.get(VspKeys.CFG_LOG_PATH)
        logCollectotInstance.SetLogPath(logPath)
        logMaxFiles = msgDict.get(VspKeys.CFG_LOG_MAX_FILES)
        logCollectotInstance.SetMaxBackupFiles(logMaxFiles)
        rotateCount = msgDict.get(VspKeys.CFG_LOG_ROTATE_COUNT)
        logCollectotInstance.SetRotateCount(rotateCount)

    def __UpdateStatsParams(self):
        msgDict = self.__message.msgDict
        statsInstance = VSPStats()
        statsPath = msgDict.get(VspKeys.CFG_STATS_PATH)
        statsInstance.SetPath(statsPath)
        refreshRate = msgDict.get(VspKeys.CFG_STATS_REFRESH_RATE)
        statsInstance.SetRefrestRate(refreshRate)

    def __UpdateIaeAgentsConfigFiles(self):
        msgDict = self.__message.msgDict
        logPathParams = msgDict.get(VspKeys.CFG_LANG_UPDATE_LOG_PATH)
        logLevelParams = msgDict.get(VspKeys.CFG_LANG_UPDATE_LOG_LEVEL)
        if logPathParams is None:
            if logLevelParams is None:
                return
        values = None
        keys = None
        editFieldKey = None
        if logPathParams is not None:
            values = logPathParams
            keys = VspKeys.CFG_LANG_UPDATE_LOG_PATH
            editFieldKey = VspKeys.CFG_LOG_PATH
        if logLevelParams is not None:
            values = logLevelParams
            keys = VspKeys.CFG_LANG_UPDATE_LOG_LEVEL
            editFieldKey = VspKeys.CFG_LOG_LEVEL
        listKeys = keys.split(':')
        listValues = values.split(':', 2)
        if len(listKeys) is not len(listValues):
            logging.warn('values are not in correct order %s' % values)
            return None
        paramsDict = {}
        for i in range(len(listKeys)):
            paramsDict[listKeys[i]] = listValues[i]
        else:
            appContext = paramsDict[VspKeys.PD_KEY_CONTEXT_PATH]
            processType = str(paramsDict[VspKeys.PD_KEY_PROCESS_TYPE]).lower()
            editField = paramsDict[editFieldKey]
            if len(editField) == 0 or len(processType) == 0:
                logging.warn('input values are empty')
                return None
            if MessageCache().IsPresent(appContext) is False:
                logging.warning('app context %s is not present' % appContext)
                return None
            msgDict =  MessageCache().GetMessage(appContext).msgDict
            appDeploymentFolder = msgDict.get(VspKeys.PD_KEY_APP_PATH, [])[0]
            restartCommand =  msgDict.get(VspKeys.PD_KEY_WEB_SERVER_CMD, '')
            param = editFieldKey + ':' + editField
            status = updateConfFile(processType, appContext, param, appDeploymentFolder, restartCommand)
            if status is True:
                # Note: a process can have lot of app context and each app context can have different config valuse
                key = processType + ":" + appContext  + ":" + editFieldKey
                IaeConfigCache().Insert(key, editField)
        return False

    def GetFeedbackMsg(self):
        return {}

class ProvisionMessageProcessor(messages.Error):
    __message = None
    __message: messages.ProvisionMessage
    __feedbackMsg:dict = {}

    def __init__(self, message: messages.ProvisionMessage):
        self.__message = message

    def __Validate(self):
        # Check if app deploytment folder is present or not for app service
        serviceType = self.__message.GetMsgDictValue(VspKeys.PD_KEY_SERVICE_TYPE)
        if serviceType == VspKeys.SERVICE_TYPE_APP:
            appDepList = self.__message.GetMsgDictValue(VspKeys.PD_KEY_APP_PATH)
            if appDepList is None or len(appDepList) == 0:
                error = "application deployment path is empty"
                self.SetError(error)
                logging.critical(error)
                return False
            elif appDepList is not None:
                path = self.__message.msgDict.get(VspKeys.PD_KEY_APP_PATH)[0]
                if not os.path.isdir(path):
                    error = "application deployment path %s is not present" % path
                    self.SetError(error)
                    logging.critical(error)
                    return False

        return True

    def ProcessMessage(self):
        if self.__Validate() is not True:
            logging.info('Failed validate check')
            return False
        self.auxFlags = self.__message.GetAuxilaryFlags()
        self.skipShm =  True if self.auxFlags & messages.AuxilaryInfo.AUX_FLAG_SKIP_SHM_CREATION else False
        self.containerDeployment =  True if (self.__message.Get(VspKeys.PD_KEY_DEPLOYMENT_TYPE) ==
                           VspKeys.PD_VAL_DEPLOYMENT_TYPE_CONTAINER) else False

        logging.debug('ProvisionMessageProcessor processing with aux flags %d' % self.auxFlags)
        status = False

        # If skip shm flag is not set and deployment type is container just create the shm
        skipProvision = False
        if self.containerDeployment:
            if not self.skipShm:
                skipProvision = True
        # VM
        else:
            autoprovFlag =  self.__message.msgDict.get(VspKeys.PD_KEY_AUTOPROV_FLAG, True)
            if autoprovFlag is False:
                skipProvision = True
        if skipProvision:
            self.__message.SetAuxilaryFlags(self.auxFlags |
                                messages.AuxilaryInfo.AUX_FLAG_SKIP_PROVISION)

        if self.auxFlags & messages.AuxilaryInfo.AUX_FLAG_DEFAULT_PROCESSING:
            status = self.Process()
        elif self.auxFlags & messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP:
            status = self.Cleanup()
        return status

    def Process(self):
        appContext = self.__message.msgDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
        nameSapceId = self.__message.msgDict.get(VspKeys.PD_KEY_NAMESPACE, None)
        mapVersion = 1
        status = True
        if appContext is None:
            error = 'app context not found'
            logging.critical(error)
            self.__message.SetError(error)
            return False
        if MessageCache().IsPresent(appContext) is False:
            logging.debug("trying to allocate shared memory for %s" % appContext)
            autoProvBuilder = autoprovbuilder.BuildAutoprov(self.__message)
            autoprov = autoProvBuilder.Build()
            if autoprov is None:
                return False
            if self.auxFlags & messages.AuxilaryInfo.AUX_FLAG_SKIP_PROVISION:
                 logging.info('skipping provision for app context %s' % appContext)
            else:
                # Do unprovision/cleanup first before doing the provision for the first time
                autoprov.message.SetAuxilaryFlags(messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP | 
                                                  messages.AuxilaryInfo.AUX_FLAG_SKIP_REFCOUNT_CHANGE)
                # fail or success doesn't matter for cleanup
                status = autoprov.Autoprov()
                logging.info("cleanup before actual provision status is  %d" % status)
                autoprov.message.SetAuxilaryFlags(messages.AuxilaryInfo.AUX_FLAG_DEFAULT_PROCESSING)
                status = autoprov.Autoprov()

            if status is True:
                success = True
                if self.skipShm is False:
                    success = IaeAssistLibrary().AllocateShm(appContext)
                elif self.skipShm is True:
                    logging.info("skipping shared memroy allocation for app context %s" % appContext)
                if success is False:
                    error = "failed shared memroy allocation for app context %s" % appContext
                    logging.critical(error)
                    self.__message.SetError(error)
                    return False
                MessageCache().Insert(appContext, self.__message)
                NameSpaceCache().Insert(nameSapceId, appContext)
            elif status is False:
                error = "provision for app context %s failed" % appContext
                logging.critical(error)
                self.__message.SetError(error)
                return False

        # Increment the running map version
        cachedMessage =  MessageCache().GetMessage(appContext)
        if cachedMessage is not None:
            if cachedMessage.iaePbConfig.common.runningMapVersion != 0:
                mapVersion = cachedMessage.iaePbConfig.common.runningMapVersion
            self.__message.iaePbConfig.common.runningMapVersion = mapVersion + 1
            logging.debug("updated running map version to %d",
                         self.__message.iaePbConfig.common.runningMapVersion)

        # Serialized protobuf data
        protoData = self.__message.iaePbConfig.SerializeToString()
        logging.debug("serialized data size is %d" % len(protoData))

        if self.skipShm is False:
            logging.debug("trying to update shared memory for %s" % appContext)
            status = IaeAssistLibrary().UpdateShm(appContext, protoData, mapVersion)
        elif self.skipShm is True:
            logging.info("skipping shared memroy update for app context %s" % appContext)
        if status is True:
            vsputils.SaveConfgJsonFile(nameSapceId, self.__message.GetParentDict())
            MessageCache().Update(appContext, self.__message)
        elif status is False:
            error = "failed shared memroy update for app context %s" % appContext
            logging.critical(error)
            self.__message.SetError(error)
        return status

    def Cleanup(self):
        unprovProcessor = UnprovisionMessageProcessor(messages.UnprovisionMessage(self.__message.GetParentDict()))
        appContext = self.__message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
        if unprovProcessor.Unprovision(self.__message) is not False:
            logging.info('cleanup success for app context %s', appContext)
            return True
        error = 'cleanup failed for app context %s', appContext
        logging.warning(error)
        self.__message.SetError(error)
        return False

    def GetFeedbackMsg(self):
        if self.containerDeployment:
            self.__feedbackMsg[VspKeys.PD_KEY_APP_COLLECTIVE_ID] = self.__message.GetMsgDictValue(
                VspKeys.PD_KEY_APP_COLLECTIVE_ID)
            self.__feedbackMsg["reason"] = self.GetError()
        else:
            self.__feedbackMsg[VspKeys.PD_KEY_ASI_ID] = self.__message.Get(VspKeys.PD_KEY_ASI_ID)
            self.__feedbackMsg[VspKeys.PD_KEY_NAMESPACE] = self.__message.msgDict.get(VspKeys.PD_KEY_NAMESPACE , -1)
            self.__feedbackMsg[VspKeys.PD_KEY_REQUEST_ID] = self.__message.msgDict.get(VspKeys.PD_KEY_REQUEST_ID , -2) + 1

        if self.__message.IsErrorSet():
            self.__feedbackMsg[VspKeys.PD_KEY_ERROR_MESSAGE] = self.__message.GetError()

        logging.debug("added dict %s to feedback msg" %  self.__feedbackMsg)
        return self.__feedbackMsg

class ProcessControlMessageProcessor(messages.Error):
    __message = None
    __message: messages.ProcessControlMessage
    __feedbackMsg:dict = {}
    def __init__(self, message: messages.ProcessControlMessage):
        self.__message = message

    def __Validate(self):
        return True

    def ProcessMessage(self):
        if self.__Validate() is not True:
            logging.info('Failed validate check')
            return False
        logging.debug('ProcessControlMessageProcessor processing message')
        keys =  MessageCache().GetCacheKeys()

        for key in keys:
            logging.debug('key is %s size %d' % (key, len(keys)))
            cachedMessage = MessageCache().GetMessage(key)
            if cachedMessage is not None:
                if isinstance(cachedMessage, messages.ProcessControlMessage) is True:
                    logging.debug("got messsage of type %s" , type(message))
                    continue
                cachedMessage.SetAuxilaryFlags(AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP)
                logging.debug('message type is  %s' % cachedMessage.Get(VspKeys.PD_KEY_MSG_TYPE))
                if cachedMessage.Get(VspKeys.PD_KEY_MSG_TYPE) is 2:
                    continue
                msgProcessorBuilder = msgprocessor.BuildMessageProcessor(cachedMessage)
                msgProcessor = msgProcessorBuilder.Build()
                if msgProcessor is not None:
                    if msgProcessor.ProcessMessage() is True:
                        logging.debug('success: processed message named %s of type %s' % (
                         key, type(cachedMessage)))
                    else:
                        logging.debug('failed: processing message named %s of type %s' % (
                         key, type(cachedMessage)))
                MessageCache().RemoveAll()
        logging.info('calling EXIT')
        os._exit(0)

    def GetFeedbackMsg(self):
        return {}

class UnprovisionMessageProcessor(messages.Error):
    __message = None
    __message: messages.UnprovisionMessage
    __feedbackMsg:dict = {}
    def __init__(self, message: messages.UnprovisionMessage):
        self.__message = message

    def __Validate(self):
        return True

    def ProcessMessage(self):
        """ From namespace cache get all the appContext and from MessageCache get
           all the messages and perform unprovision by setting aux flag cleanup
        """
        if self.__Validate() is not True:
            logging.info('Failed validate check')
            return False
        logging.debug('UnprovisionMessageProcessor processing message')
        nameSpaceId = self.__message.GetMsgDictValue(VspKeys.PD_KEY_NAMESPACE)
        if nameSpaceId is None:
            logging.warn('namespace not found')
            return False
        appContexts = NameSpaceCache().GetAppContexts(nameSpaceId)
        for appContext in appContexts:
            message = MessageCache().GetMessage(appContext)
            if message is None:
                logging.warn('None message for app context %s', appContext)
            else:
                message.SetAuxilaryFlags(messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP)
                if self.Unprovision(message) is False:
                    logging.info('failed unprovision for app context %s', appContext)
                NameSpaceCache().RemoveNameSpace(nameSpaceId)
        vsputils.RemoveAllConfigJsonFile()
        return True

    def Unprovision(self, message):
        if isinstance(message, messages.ProvisionMessage) is False:
            logging.debug("got messsage of type %s" , type(message))
            return False

        status = False
        if message is None:
            logging.debug('message is none')
            return False
        else:
            autoProvBuilder = autoprovbuilder.BuildAutoprov(message)
            autoprov = autoProvBuilder.Build()
            if autoprov is None:
                return False
            appContext = message.metaDataDict.get(VspKeys.PD_KEY_CONTEXT_PATH, None)
            autoprov.message.SetAuxilaryFlags(messages.AuxilaryInfo.AUX_FLAG_FORCE_CLEANUP)
            status = autoprov.Autoprov()
            if status is True:
                    logging.info('success :uprovisioned app context %s' % appContext)
            else:
                logging.warning('failed :uprovisioning app context %s' % appContext)
        IaeAssistLibrary().Clear(appContext)
        MessageCache().Remove(appContext)
        # Note app context will be unique always
        IaeConfigCache().RemoveContains(appContext)
        return status

    def GetFeedbackMsg(self):
        self.__feedbackMsg[VspKeys.PD_KEY_ASI_ID] = self.__message.Get(VspKeys.PD_KEY_ASI_ID)
        self.__feedbackMsg[VspKeys.PD_KEY_NAMESPACE] = self.__message.msgDict.get(VspKeys.PD_KEY_NAMESPACE , -1)
        self.__feedbackMsg[VspKeys.PD_KEY_REQUEST_ID] = self.__message.msgDict.get(VspKeys.PD_KEY_REQUEST_ID , -2) + 1

        if self.__message.IsErrorSet():
            self.__feedbackMsg[VspKeys.PD_KEY_ERROR_MESSAGE] = self.__message.GetError()
        
        logging.debug("added dict %s to feedback msg" %  self.__feedbackMsg)
        return self.__feedbackMsg

class InternalStateMessageProcessor(messages.Error):
    __message = None
    __message: messages.InternalStateMessage
    __feedbackMsg:dict = {}
    def __init__(self, message: messages.InternalStateMessage):
        self.__message = message

    def __Validate(self):
        return True

    def ProcessMessage(self):
        """ 
        For Internal state
        """
        if self.__Validate() is not True:
            logging.info('Failed validate check')
            return False
        stateId =  self.__message.msgDict.get(VspKeys.CFG_STATE_ID , None)
        logging.info("processing sate id %s" % stateId)
        if stateId is not None:
            if stateId == VspKeys.CFG_STATE_ID_APPCTX:
                return self.__ProcessAppCtxState()
            elif stateId == VspKeys.CFG_STATE_ID_TYPES:
                return self.__ProcessTypesState()
            elif stateId == VspKeys.CFG_STATE_ID_LOG_LEVEL:
                 return self.__ProcessLogLevelState()
            elif stateId == VspKeys.CFG_STATE_ID_CONF:
                 return self.__ProcessLogConfigState()
        return False

    def __ProcessAppCtxState(self):
        subState =  self.__message.msgDict.get(VspKeys.CFG_SUBSTATES , None)
        if subState is not None:
            self.__feedbackMsg[VspKeys.CFG_STATE] = list()
            appCtxList:dict = {}
            for state in subState:
                cache = MessageCache().GetCache()
                appCtxList[state] = list()
                for appCtx in cache.keys():
                    serviceType = cache[appCtx].GetMsgDictValue(VspKeys.PD_KEY_SERVICE_TYPE)
                    processType = None
                    logging.info('serviceType is %s for appCtx %s' % (serviceType, appCtx))
                    if serviceType is not None:
                        if serviceType == VspKeys.SERVICE_TYPE_APP:
                            processType = cache[appCtx].GetMsgDictValue(VspKeys.PD_KEY_PROCESS_TYPE)

                        elif serviceType == VspKeys.SERVICE_TYPE_WEB:
                            processType = cache[appCtx].GetMsgDictValue(VspKeys.PD_KEY_WEB_SERVER_TYPE)
                    if processType.lower() == state.lower():
                        logging.debug("found matching app context %s for process %s" %(appCtx, processType))
                        appCtxList[state].append(appCtx)
                    else:
                        logging.debug("compare failed for %s with %s" % (processType, state))
            # add the info back in feedback msg
            self.__feedbackMsg[VspKeys.CFG_STATE] = appCtxList
            logging.debug("added dict %s to feedback msg" % appCtxList)
        else:
            return False
        return True

    def __ProcessTypesState(self):
        supportedTypes = {"java", "php", "nodejs", "dotnet", "ruby", "nginx", "apache", "iae-encode"}
        typesList = dict()
        for i, types in enumerate(supportedTypes):
            typesList[str(i + 1)] =  types
        # add the info back in feedback msg
        self.__feedbackMsg[VspKeys.CFG_STATE] = typesList
        logging.debug("added dict %s to feedback msg" % typesList)
        return True

    def __ProcessLogLevelState(self):
        supportedLogLevels = list({"Info", "Trace", "Debug", "Error", "On", "Off" })
        typesList = dict()
        for i, types in enumerate(supportedLogLevels):
            typesList[str(i + 1)] = types
        # add the info back in feedback msg
        self.__feedbackMsg[VspKeys.CFG_STATE] = typesList
        logging.debug("added dict %s to feedback msg" % typesList)
        return True

    def __ProcessLogConfigState(self):
        cache = IaeConfigCache().GetCache()
        confList = dict()
        for i, key in enumerate(cache.keys()):
            val = cache[key]
            confList[str(i + 1) + ". " + key] = val
        # add the info back in feedback msg
        self.__feedbackMsg[VspKeys.CFG_STATE] = confList
        logging.debug("added dict %s to feedback msg" % confList)
        return True

    def GetFeedbackMsg(self):
        # add the required headers in the feedback msg and then return the message
        # Note 1: the message need to be sent to vsp-cli not manager VIPC_CLIENT_VCLI_ID 10009
        # Note 2: common headers like version src and dst component is handled by send api of manager
        headers:dict = {}
        headers[VspKeys.PD_KEY_SEGMENTED_RESPONSE] = False
        return {** self.__feedbackMsg, **headers}

class FilePurgeMessageProcessor(messages.Error):
    __message = None
    __message: messages.FilePurgeMessage
    __feedbackMsg:dict = {}
    def __init__(self, message: messages.FilePurgeMessage):
        self.__message = message

    def __Validate(self):
        return True

    def ProcessMessage(self):
        procesType = self.__message.GetMsgDictValue(VspKeys.PD_KEY_PROCESS_TYPE)
        if procesType is None:
            logging.warning("invalid process type")
            return False
        if procesType is VspKeys.APPLICATION_PHP:
            return self.__ProcessPhp(procesType)
        return True

    def __ProcessPhp(self, procesType:str):
        logging.debug("file purging stared for %s" % procesType)
        # purge the files created on log location
        map = IaeConfigCache().GetCache()
        keys = list(map.keys())
        logPath = None
        part = procesType
        for key in keys:
            if part in key:
                if VspKeys.CFG_LOG_PATH in key:
                    logPath = IaeConfigCache().GetMessage(key)
                    logging.debug("got log path as %s" % logPath)

        if logPath is not None and os.path.exists(logPath):
            for rootFolder, folders, files in os.walk(logPath):
                for file in files:
                    filePath = os.path.join(root_folder, file)
	                # specify the days
                    days = 3
	                # converting days to seconds
	                # time.time() returns current time in seconds
                    seconds = time.time() - (days * 24 * 60 * 60)
                    # comparing the days
                    if seconds >= self.__GetAge(filePath):
                        self.__RemoveFile(filePath)
        else:
            logging.debug(f'"{logPath}" is not found')
            return False

        return True

    def __GetAge(path):
	    # getting ctime of the file/folder
	    # time will be in seconds
        ctime = os.stat(path).st_ctime
	    # returning the time
        return ctime

    def __RemoveFile(self, path):
    	# removing the file
        try:
            if not os.remove(path):
    	    	# success message
                logging.debug(f"{path} is removed successfully")
            else:
    	    	# failure message
                logging.warning(f"Unable to delete the {path}")
        except os.error:
            logging.warning(f"Unable to delete the {path} reason-> {os.error.strerror}")
