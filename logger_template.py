import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
TRACE = logging.DEBUG + 5
logging.addLevelName(TRACE, 'TRACE')
logging.TRACE = TRACE

def trace(self, message, *args, **kws):
    (self._log)(TRACE, message, args, **kws)


logging.Logger.trace = trace
runningLogCount = 1
MAX_LOG_ENRTY = 10

class LogCollector(logging.Handler, logging.Filter):
    __handler = None
    __handler: logging.handlers.RotatingFileHandler
    __logPath = None
    __logPath: str
    __logLevel = 'INFO'
    __logLevel: str
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(LogCollector, cls).__new__(cls)
        return cls.__instance

    def setup_logging(self, verbosity=0, log_file=None, max_log_size=5000000, log_rotation_count=20):
        """
        Setup logging
        :param verbosity: verbosity level. <0 is ERROR, 0 is normal (WARNING), 1 is INFO, >1 is DEBUG
        :return: logger instance. You likely won't need it, just use the logging module directly.
        """
        log_path = None
        if log_file is not None:
            if log_file.rfind(os.path.sep) != -1:
                log_path = log_file[0:log_file.rfind(os.path.sep)]
            if log_path is not None:
                try:
                    Path(log_path).mkdir(parents=True, exist_ok=True)
                except:
                    logging.error('Exception occurred while trying to create log path: {}'.format(log_path))
                    logger = logging.getLogger()
                    logger.disabled = True
                    return logger
                else:
                    self.__logPath = log_path
        
        self.__AddHandler(log_file, max_log_size, log_rotation_count)
        self.__AddFormatter()
        self.__AddFilter()
        
        rootLogger = logging.getLogger()
        
        if verbosity > 1:
            rootLogger.setLevel(logging.DEBUG)
        elif verbosity == 1:
            rootLogger.setLevel(logging.INFO)
        else:
            if verbosity == 0:
                rootLogger.setLevel(logging.WARNING)
            else:
                if verbosity < 0:
                    rootLogger.setLevel(logging.ERROR)
        return rootLogger

    def __AddHandler(self, log_file=None, max_log_size=5000000, log_rotation_count=20):
        self.__handler = RotatingFileHandler(log_file,
          maxBytes=max_log_size, backupCount=log_rotation_count, mode='a')
        rootLogger = logging.getLogger()
        rootLogger.addHandler(self.__handler)
        rootLogger.addHandler(LogCollector())
        # remove std out handler
        logging.getLogger().removeHandler(logging.getLogger().handlers[0])

    def __AddFormatter(self):
        logFormatter = logging.Formatter('%(asctime)s | WEB | %(levelname)s | %(process)d |%(filename)s:%(lineno)s - %(funcName)s() | %(message)s')
        self.__handler.setFormatter(logFormatter)

    def __AddFilter(self):
        rootLogger = logging.getLogger()
        rootLogger.addFilter(LogCollector())

    def GetLogLevel(self, level: str):
        level = level.lower()
        if level in ('info', 'information'):
            return logging.INFO
        if level in ('warn', 'warning'):
            return logging.WARNING
        if level in ('error', ):
            return logging.ERROR
        if level in ('debug', 'debuggin'):
            return logging.DEBUG
        if level in ('trace', 'Tracing'):
            return logging.TRACE
        return logging.INFO

    def SetLogPath(self, path: str):
        if self.__logPath is None or path is None:
            return
        if self.__logPath == path:
            logging.debug('no change in log path %s' % path)
            return None
        self.__handler.stream

    def SetLogLevel(self, level: str):
        if self.__logLevel is None or level is None:
            return
        if self.__logLevel == level:
            return
        logLevel = self.GetLogLevel(level)
        rootLogger = logging.getLogger()
        rootLogger.setLevel(logLevel)
        logging.info('changed log level from %s to %s' % (self.__logLevel, level))

    def GetDefaultAbsLogFileName(self):
        if os.name == 'nt':
            return 'C:\\Program Files (x86)\\Virsec\\log\\web-assist\\web-assist.log'
        return '/var/virsec/log/web-assist/web-assist.log'

    def SetMaxLogSize(self, size: int):
        if self.__handler is None:
            return
        self.__handler.maxBytes = size

    def SetMaxBackupFiles(self, count: int):
        if self.__handler is None:
            return
        self.__handler.backupCount = count

    def SetRotateCount(self, count: int):
        pass

    def emit(self, record):
        """
       call back method
       """
        #print(record.count)
        if record.count >= MAX_LOG_ENRTY:
            record.count = 0

    def filter(self, record):
        """
        call back method
        """
        global runningLogCount
        record.count = runningLogCount
        runningLogCount += 1
        return True
