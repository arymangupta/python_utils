import msgprocessor
import messagebuilder
import logging
from vsp_defines import VSPInfo
import messages
import json
import os
import validatemessage
import re
def ProcessInputJsonMessage(jsonMsg = None , jsonDict:dict=None, filePath: str=None,
                           flags=messages.AuxilaryInfo.AUX_FLAG_DEFAULT_PROCESSING):
    # try purging the log file, failure doesn't matter
    TryPurgeLogFile()
    processedCount = 0
    feedBackmsg = {}
    factoryMsgBuilder = messagebuilder.FactoryMessageBuilder(jsonMsg=jsonMsg, jsonDict=jsonDict, filePath=filePath)
    if factoryMsgBuilder is None:
        return processedCount
    msgBuilder = factoryMsgBuilder.BuildMessageBuilder()
    if msgBuilder is not None:
        buitMessages = msgBuilder.BuildMessage()
        if buitMessages is not None:
            logging.debug("buitMessages size %d" , len(buitMessages))
            # Validate built messages list
            validate = validatemessage.Validate()
            if not validate.CheckAppContextUniqness(buitMessages):
                feedBackmsg = validate.GetFeedbackMsg()
                return -1, feedBackmsg

            for message in buitMessages:
                message.SetAuxilaryFlags(flags)
                msgProcessorBuilder = msgprocessor.BuildMessageProcessor(message)
                msgProcessor = msgProcessorBuilder.Build()
                if msgProcessor is not None:
                    status = msgProcessor.ProcessMessage()
                    if status is True:
                        logging.debug("success processed message of type %s" , type(message))
                        processedCount += 1
                        feedBackmsg = msgProcessor.GetFeedbackMsg()
                    else:
                        logging.critical("failed processing message of type %s" , type(message))
                        feedBackmsg = msgProcessor.GetFeedbackMsg()
                        return -1, feedBackmsg

    return processedCount, feedBackmsg


def SaveConfgJsonFile(nameSpace:str , jsonMsg:dict):
    if nameSpace is None:
        return
    fileName = "config-" + nameSpace + ".json"
    fileLoc = os.path.join(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH , fileName)
    if (os.path.isdir(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH)):
            with open(os.path.join(fileLoc), 'w' , encoding='utf-8') as f:
                json.dump(jsonMsg, f , indent=4)
                f.close()
                logging.debug("saved json contents at %s" % fileLoc)


def RemoveConfigJsonFile(nameSpace:str , fileName = None):
    if fileName is None:
        fileName = "config-" + nameSpace + ".json"
    fileLoc = os.path.join(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH , fileName)
    if (os.path.isfile(fileLoc)):
        logging.debug("Removing file %s" % fileLoc)
        os.remove(fileLoc)

def RemoveAllConfigJsonFile():
    jsonList:str = []
    listOfFiles = []
    if os.path.isdir(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH):
        for f in os.listdir(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH):
           logging.debug("list of files to remove %s" % f)
           if os.path.isfile(os.path.join(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH, f)):
               listOfFiles.append(f)
        logging.debug("list of files to remove %s" % listOfFiles)   
        for file in listOfFiles:
            RemoveConfigJsonFile("" , file)

def GetSavedConfigJson():
    jsonList:str = []
    listOfFiles = []
    if os.path.isdir(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH):
        for f in os.listdir(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH):
           if os.path.isfile(os.path.join(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH, f)):
               listOfFiles.append(f)
        
        for file in listOfFiles:
            fileLoc = os.path.join(VSPInfo.WEB_ASSIST_SAVED_CONFIG_PATH , file)
            logging.debug("reading file %s" % fileLoc)
            with open(fileLoc, "r" , encoding='utf-8') as f:
                contents = f.read()
                msg = json.loads(contents)    
                logging.debug("file contents for %s are %s" % (fileLoc, contents))
                jsonList.append(msg)
                f.close()
    return jsonList

def Versiontuple(v:str):
    filled = list()
    if v is None:
        v = "0.0.0"
    for point in v.split("."):
       filled.append(point.zfill(8))
    return tuple(filled)

def TryPurgeLogFile():
    builder = messagebuilder.FilePurgeMessageBuilder(dict())
    messageList = builder.BuildMessage()
    if messageList is not None:
        for message in messageList:
            msgProcessor = msgprocessor.FilePurgeMessageProcessor(message)
            if msgProcessor is not None:
                 return msgProcessor.ProcessMessage()
    return False