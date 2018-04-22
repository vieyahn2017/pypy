import logging
from constants import *
from datetime import datetime

L_DEBUG = logging.DEBUG
L_ERROR = logging.ERROR
L_INFO = logging.INFO
L_WARN = logging.WARNING
L_CRITICAL = logging.CRITICAL
LEVELS = {'DEBUG': L_DEBUG,
          'INFO': L_INFO,
          'WARNING': L_WARN,
          'ERROR': L_ERROR,
          'CRITICAL': L_CRITICAL}
LOGGERS = {'main': 'iscsiadmin-main'}


class IscsiAdminLogger(logging.Logger):
    def __init__(self, name, level=L_DEBUG):
        logging.Logger.__init__(self, name, level)
        self.__printtostd = False

        try:
            loghandler = logging.FileHandler(LOGLOC)
            logformatter = logging.Formatter("%(message)s")
            loghandler.setFormatter(logformatter)
            self.addHandler(loghandler)
        except Exception, error:
            print error
            raise RuntimeError("Could not set up logger for iscsiadmin-main")

    @property
    def get_print_to_std(self):
        return self.__printtostd

    @get_print_to_std.setter
    def set_print_to_std(self, value):
        self.__printtostd = value

    def logmsg(self, severity, message):
        now = datetime.now().strftime('%b %d %H:%M:%S')
        level = self.getEffectiveLevel()
        if level <= LEVELS[severity]:
            msgentry = "%s : %s : %s" % (now, severity, message)
            self.log(LEVELS[severity], msgentry)
            if self.__printtostd:
                print(msgentry)

    @staticmethod
    def getlogger():
        logging.setLoggerClass(IscsiAdminLogger)
        logger = logging.getLogger(LOGGERS['main'])
        logging.setLoggerClass(logging.Logger)
        return logger
