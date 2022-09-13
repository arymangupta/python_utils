from ctypes import *
import logging
from googleproto.IAE_Configs_pb2 import IAE_PB_CONFIG

class IaeAssistLibrary:
    __ENCODING = 'utf-8'
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(IaeAssistLibrary, cls).__new__(cls)
        return cls.__instance

    __iaeAssistLib = None
    __isLoaded = False
    __libPath: str

    def Load(self , libPath:str):
        if self.__isLoaded:
          logging.info("iae-assist library is already loaded from path %s" 
                       % self.__libPath)
          return self.__iaeAssistLib
        if libPath is None:
            logging.warning("invalid parameter path is None")
            return None
        try:
            self.__iaeAssistLib = cdll.LoadLibrary(libPath)
        except Exception as e:
            logging.error(
                f"LoadLibrary for {libPath} raised exception: {e}"
            )
            return None

        if not self.__iaeAssistLib:
            logging.error(
                "iae assist library is not loaded from %s" % libPath
            )
            return None
        logging.info(
                f"success LoadLibrary for {libPath}"
            )
        self.__isLoaded = True
        self.__libPath = libPath
        return self.__iaeAssistLib
        
    def Unload(self):
        if self.__isLoaded:
            self.__isLoaded = False
            self.__libPath = None
            self.__iaeAssistLib = None

    def Get(self):
        if self.__isLoaded is False:
            logging.warn("iae-assist library is not loaded")
            self.Unload()
            return None
        return self.__iaeAssistLib

    def AllocateShm(self, memName:str):
        # ism_allocate(const char* mem_name);
        if self.__isLoaded is False:
            logging.warn("iae-assist library is not loaded")
            return False
        
        if memName is None:
            logging.error("invalid paramerter")
            return False
        
        try:
            outMemName = c_char_p(memName.encode(self.__ENCODING))
            rval = self.__iaeAssistLib.ism_allocate(outMemName)
        except Exception as e:
            logging.error(
                f"ism_allocate for {self.__libPath} raised exception: {e}"
            )
            return False
        if rval:
            logging.warning("allocate failed with error %d" % rval)
            return False
        logging.info(
                f"success Allocated shared memory for {memName}"
            )
        return True                
    
    def UpdateShm(self, memName:str, data:bytes, mapVersion:int):
        # int ism_update(const char* mem_name, const char* data_pointer, uint32_t data_size);
        if self.__isLoaded is False:
            logging.warn("iae-assist library is not loaded")
            return False
        
        if memName is None or data is None or mapVersion is None:
            logging.error("invalid paramerters")
            return False
        outDataSize = -1
        try:
            outMemName = c_char_p(memName.encode(self.__ENCODING))
            outData = c_char_p(data)
            outDataSize = c_int(len(data))
            outMapVersion = c_int(mapVersion)
            rval = self.__iaeAssistLib.ism_update(outMemName, outData, outDataSize, outMapVersion)
        except Exception as e:
            logging.error(
                f"ism_update for {self.__libPath} raised exception: {e}"
            )
            return False
        if rval:
            logging.warning("update memory failed with error %d" % rval)
            return False        
        logging.info(
                f"success updated memory for {memName} having size {outDataSize}"
            )
        return True
    
    def Clear(self, memName:str):
        # int ism_clear(const char* mem_name, void* ptr);
        if self.__isLoaded is False:
            logging.warn("iae-assist library is not loaded")
            return False
        
        if memName is None:
            logging.error("invalid paramerters")
            return False
        try:
            outMemName = c_char_p(memName.encode(self.__ENCODING))
            outShmPtr = None
            rval = self.__iaeAssistLib.ism_clear(outMemName , outShmPtr)
        except Exception as e:
            logging.error(
                f"ism_clear for {self.__libPath} raised exception: {e}"
            )
            return False
        if rval:
            logging.warning("clear memory failed with error %d" % rval)
            return False          
        logging.info(
                f"success cleaned memory for {memName}"
            )
        return True
    
    def ReadShm(self, memName:str, msgSize:int=5*1024, skipParsing=False):
        # int ism_clear(const char* mem_name, void* ptr);
        if self.__isLoaded is False:
            logging.warn("iae-assist library is not loaded")
            return "iae-assist library is not loaded"
        
        if memName is None:
            logging.error("invalid paramerters")
            return "invalid paramerters"
        try:
            outMemName = c_char_p(memName.encode(self.__ENCODING))
            outMsg = create_string_buffer(msgSize)
            outMsgLen = c_int(msgSize)
            rval = self.__iaeAssistLib.icc_get_job_config(outMemName , c_int(-1), byref(outMsg), byref(outMsgLen))
        except Exception as e:
            logging.error(
                f"ism_read for {self.__libPath} raised exception: {e}"
            )
            return str("failed reading data for memory %s" %  memName)
        if rval:
            logging.warning("read memory failed with error %d" % rval)
            return "failed read memory " + memName + " errno:" + str(rval)      
        logging.info(
                f"success read data for {memName}"
            )
        if skipParsing:
            logging.info("skipped parsing")
            return outMsg.value
        mylist = IAE_PB_CONFIG()
        mylist.ParseFromString(bytes(outMsg.value))
        return ("shm data for " + memName + " having size "+
                str(outMsgLen.value) + " is\n" + str(mylist))