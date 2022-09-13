# uncompyle6 version 3.8.0
# Python bytecode 3.8.0 (3413)
# Decompiled from: Python 3.6.8 (default, Nov 16 2020, 16:55:22) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /media/sf_git/git.vsp/CVEAssist/src/PyCVE-Assist/cache.py
# Compiled at: 2022-04-06 16:25:23
# Size of source mod 2**32: 5562 bytes
import logging, msgprocessor
from messages import AuxilaryInfo, Message
from vsp_defines import VSPInfo, VspKeys, VSPComponent
class MessageCache:
    __map:dict = {}
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(MessageCache, cls).__new__(cls)
        return cls.__instance

    def Insert(self, appContext: str, message):
        present = self.__map.get(appContext, False)
        if not present:
            self.__map[appContext] = message
            logging.info('added app context %s with message type %s' % (appContext, type(message)))
            logging.debug('message contents are %s' % message.msgDict)
            logging.debug('message type is  %s' % message.commonHdrMsgDict)
            

    def Update(self, appContext: str, message):
        present = self.__map.get(appContext, False)
        if present is not False:
            self.__map[appContext] = message
            logging.debug('updated message contents are %s' % message.msgDict)

    def GetMessage(self, appContext: str):
        message = self.__map.get(appContext, None)
        logging.debug('message contents are %s' % message.msgDict)
        logging.debug('message type is  %s' % message.commonHdrMsgDict)
        return message

    def IsPresent(self, appContext: str):
        present = self.__map.get(appContext, False)
        if not present:
            return False
        return True

    def Remove(self, appContext: str):
        present = self.__map.get(appContext, False)
        if not present:
            logging.debug('no app context %s is present' % appContext)
            return None
        message = self.__map.pop(appContext, None)
        logging.info('removed app context %s having message type %s' % (appContext, type(message)))
        return message

    def RemoveAll(self):
        keys = list(self.__map.keys())
        for key in keys:
            self.Remove(key)

    def GetCache(self):
        return self.__map

    def GetCacheKeys(self):
        return list(self.__map.keys())

class NameSpaceCache:
    __map:dict = {}
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(NameSpaceCache, cls).__new__(cls)
        return cls.__instance

    def Insert(self, namespaceId: str, appContext: str):
        if str.isdigit(namespaceId) is False:
            logging.debug("namesapce is not valid %s" % namespaceId)
            return
        present = self.__map.get(namespaceId, False)
        if not present:
            self.__map[namespaceId] = set()
        self.__map[namespaceId].add(appContext)
        logging.info('added app context %s in namespace %s' % (appContext, namespaceId))

    def GetAppContexts(self, namespaceId: str):
        return list(self.__map.get(namespaceId, list()))

    def IsAppContextPresent(self, appContext: str):
        for key in self.__map.keys():
            for cachedAppCtx in self.__map[key]:
                if appContext == cachedAppCtx:
                    logging.info('found app context %s in namespace %s' % (appContext, key))
                    return key
        return None

    def RemoveNameSpace(self, namespaceId: str):
        present = self.__map.get(namespaceId, False)
        if not present:
            logging.debug('no app namespace %s is present' % namespaceId)
            return None
        appctxs = self.__map.pop(namespaceId, None)
        logging.info('removed namespace %s  having app contexts type %s' % (namespaceId, appctxs))
        return appctxs

    def RemoveAllNamespace(self):
        keys = list(self.__map.keys())
        for key in keys:
            self.RemoveNameSpace(key)
        else:
            return keys

    def RemoveAppContext(self, appContext: str):
        for key in self.__map.keys():
            for cachedAppCtx in self.__map[key]:
                if appContext == cachedAppCtx:
                    self.__map[key].remove(appContext)
                    logging.info('removed app context %s from namespace %s' % (appContext, key))
                    return key

    def GetAllAppContexts(self):
        appContexts = list()
        for key in self.__map.keys():
            for appcontex in list(self.__map.get(key, [])):
                appContexts.append (appcontex)
                logging.debug('appended appcontext %s' % appcontex)
        return appContexts

    def IsPresent(self, nameSpaceId: str):
        if self.__map.get(nameSpaceId, False) is False:
            return False
        return True

class RefCountCache:
    __map:dict = {}
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RefCountCache, cls).__new__(cls)
        return cls.__instance

    def Insert(self, entry: str):
        present = self.__map.get(entry, False)
        if not present:
            self.__map[entry] = 1
            logging.info('added entry %s with ref count %s' % (entry,
             self.__map[entry]))

    def Incr(self, entry: str):
        present = self.__map.get(entry, False)
        if not present:
            self.Insert(entry)
            return None
        self.__map[entry] += 1
        logging.debug('for entry %s ref count is %s' % (entry,
         self.__map[entry]))

    def Decr(self, entry: str):
        present = self.__map.get(entry, False)
        if not present:
            return 0
        if self.GetCount(entry) <= 0:
            self.Remove(entry)
            return -1
        logging.debug('for entry %s ref count is %s' % (entry,
         self.__map[entry] - 1))
        self.__map[entry] -= 1
        return self.__map[entry]

    def GetCount(self, entry: str):
        present = self.__map.get(entry, False)
        if not present:
            return 0
        return self.__map[entry]

    def Remove(self, entry: str):
        present = self.__map.get(entry, False)
        if not present:
            return
        logging.debug('removed entry %s having ref count %s ' % (entry,
         self.__map[entry]))
        return self.__map.pop(entry)

    def RemoveAll(self):
        keys = list(self.__map.keys())
        for key in keys:
            self.Remove(key)

# Similar to message cache
class IaeConfigCache:
    __map:dict = {}
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(IaeConfigCache, cls).__new__(cls)
        return cls.__instance

    def Insert(self, keyName: str, entry):
        present = self.__map.get(keyName, False)
        if not present:
            self.__map[keyName] = entry
            logging.info('added app context %s with message type %s' % (keyName, type(entry)))
            logging.debug(' entry contents are %s' % entry)

    def GetMessage(self, keyName: str):
        entry = self.__map.get(keyName, None)
        logging.debug(' entry contents are %s' % entry)
        return entry

    def IsPresent(self, keyName: str):
        present = self.__map.get(keyName, False)
        if not present:
            return False
        return True

    def Remove(self, keyName: str):
        present = self.__map.get(keyName, False)
        if not present:
            logging.debug('no key %s is present' % keyName)
            return None
        entry = self.__map.pop(keyName, None)
        logging.info('removed keyt %s having entry type %s' % (keyName, type(entry)))
        return entry

    def RemoveAll(self):
        keys = list(self.__map.keys())
        for key in keys:
            self.Remove(key)

    def GetCache(self):
        return self.__map

    def RemoveContains(self, part:str):
        keys = list(self.__map.keys())
        for key in keys:
            if part in key:
                self.Remove(key)