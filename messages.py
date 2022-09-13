import json
from vsp_defines import VSPInfo, VspKeys
import os, logging
from googleproto.IAE_Configs_pb2 import *

class Error:
    __error:str = str()

    def GetError(self):
        return self.__error

    def SetError(self, error:str):
        self.__error = error
        logging.debug("set error to {%s}" % self.__error)
        return self.__error

    def IsErrorSet(self):
        if len(self.__error) > 0:
            return True
        return False

class AuxilaryInfo:
    AUX_FLAG_RESET = 0
    AUX_FLAG_DEFAULT_PROCESSING = 1
    AUX_FLAG_FORCE_CLEANUP = 2
    AUX_FLAG_SKIP_PROVISION = 4
    AUX_FLAG_SKIP_SHM_CREATION = 8
    AUX_FLAG_DEPLOYMENT_CONTAINER = 16
    AUX_FLAG_SKIP_REFCOUNT_CHANGE = 32

    __flags = AUX_FLAG_DEFAULT_PROCESSING

    def GetAuxilaryFlags(self):
        return self.__flags

    def SetAuxilaryFlags(self, flags: int):
        self.__flags = flags
        logging.debug('set aux flag as %d' % self.__flags)
        return self.__flags

    def ResetAuxilaryFlags(self):
        self.__flags = 0


class Message(AuxilaryInfo, Error):
    __parentJsonDict:dict = {}
    commonHdrMsgDict:dict = {}

    def GetParentDict(self):
        return self.__parentJsonDict

    def SetParentDict(self , msgDict: dict):
        self.__parentJsonDict = msgDict

    def __str__(self):
        return 'common header {self.commonHdrMsgDict}'.format(self=self)

    def Get(self, type: str):
        return self.commonHdrMsgDict.get(type, None)


class ConfigMessage(Message):
    msgDict: dict = {}

    def __init__(self, msgDict: dict):
        self.SetParentDict(msgDict)

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)

    def __str__(self):
        return super().__str__() + ' and config message {self.msgDict}'.format(self=self)


class ProvisionMessage(Message):
    iaePbConfig: IAE_PB_CONFIG
    msgDict: dict = {}
    metaDataDict: dict = {}

    def __init__(self, jsonDict: dict):
        self.SetParentDict(jsonDict)
        self.iaePbConfig = IAE_PB_CONFIG()

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)

    def SetMsgDict(self, provDict: dict):
        self.msgDict = provDict
        logging.debug('set message dictionary to %s' % self.msgDict)


class ProcessControlMessage(Message):
    msgDict: dict = {}

    def __init__(self, jsonDict: dict):
        self.SetParentDict(jsonDict)

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)


class UnprovisionMessage(Message):
    msgDict: dict = {}
    metaDataDict: dict = {}

    def __init__(self, jsonDict: dict):
        self.SetParentDict(jsonDict)

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)

class InternalStateMessage(Message):
    msgDict: dict = {}

    def __init__(self, jsonDict: dict):
        self.SetParentDict(jsonDict)

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)    

class FilePurgeMessage(Message):
    msgDict: dict = {}
    def __init__(self, jsonDict: dict):
        self.SetParentDict(jsonDict)

    def GetMsgDictValue(self, key: str):
        return self.msgDict.get(key, None)   

def test():
    my_list = IAE_PB_CONFIG()
    web = my_list.webCollectiveConfig
    app = my_list.appCollectiveConfig
    web.webServerName = 'aryaman'
    web.applicationHostName.extend(['aryaman'])
    web.applicationHostName.extend(['aryaman'])
    my_list.configType = my_list.APP_COLLECTIVE
    print(dir(my_list))
    print(dir(IAE_PB_APPCOLLECTIVE_CONFIG))
    print(dir(IAE_PB_WEBCOLLECTIVE_CONFIG))
    print(dir(IAE_PB_CONFIG_COMMON))
    print(my_list)


#test()
