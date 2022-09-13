import logging
import messages
import cache
from vsp_msg_enums import vmsg_enums
from vsp_defines import VSPComponent, VspKeys

class Validate(messages.Error):
    __feedbackMsg:dict = {}
    __message:messages.ProvisionMessage = None
    
    def CheckAppContextUniqness(self, msgLists:list):
        if msgLists is None or len(msgLists) == 0:
            return True

        appCtxSet = set()
        nameSpace = None
        # Check within namespace
        for msg in msgLists:

            if msg.Get(VspKeys.PD_KEY_MSG_TYPE) is vmsg_enums[VSPComponent.vweb_assist].get('PROV_START_JOB', 6):
                # Save any one of the messsage
                self.__message = msg
                appContext = msg.GetMsgDictValue(VspKeys.PD_KEY_CONTEXT_PATH) 
                nameSpace = msg.GetMsgDictValue(VspKeys.PD_KEY_NAMESPACE)
                logging.debug("got app context %s" % appContext)
                if appContext in appCtxSet:
                    error = "found matching app context %s within namespace %s" %(appContext, nameSpace)
                    logging.critical(error)
                    self.SetError(error)
                    return False
                else:
                    appCtxSet.add(appContext)
        
        logging.debug("available app context in namespace %s are %s" %(nameSpace, appCtxSet))
        
        # Check accross namespace
        if nameSpace is not None and cache.NameSpaceCache().IsPresent(nameSpace) is False:
            allCachedAppContext = cache.NameSpaceCache().GetAllAppContexts()
            logging.debug("all cached app contexts are %s" %(allCachedAppContext))
            for appCtx in appCtxSet:
                if appCtx in allCachedAppContext:
                    existingNamespace = cache.NameSpaceCache().IsAppContextPresent(appCtx)
                    error = "found matching app context %s already configured in namespace %s" % (appContext, existingNamespace)
                    self.SetError(error)
                    logging.critical(error)
                    return False

        return True
    

    def GetFeedbackMsg(self):
        if self.__message is None:
            return self.__feedbackMsg
        self.__feedbackMsg[VspKeys.PD_KEY_ASI_ID] = self.__message.Get(VspKeys.PD_KEY_ASI_ID)
        self.__feedbackMsg[VspKeys.PD_KEY_NAMESPACE] = self.__message.msgDict.get(VspKeys.PD_KEY_NAMESPACE , -1)
        self.__feedbackMsg[VspKeys.PD_KEY_REQUEST_ID] = self.__message.msgDict.get(VspKeys.PD_KEY_REQUEST_ID , -2) + 1
        if self.IsErrorSet():
            self.__feedbackMsg[VspKeys.PD_KEY_ERROR_MESSAGE] = self.GetError()  
        logging.debug("added dict %s to feedback msg" %  self.__feedbackMsg)
        return self.__feedbackMsg