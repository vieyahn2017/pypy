import sys
import ialogger
try:
    import gtk
except:
    print("An error occurred while importing gtk.")
    print("Please make sure you have a valid GTK+ Runtime Environment.")
    sys.exit(1)

from constants import *


class IscsiadminApp():
    def __init__(self):
        self.gladefile = mainapp_glade
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("main_window")
        self.runsetup()
        self.logger.logmsg("INFO", "Starting iscsiadmin")
        self.window.show()

    def runsetup(self):
        self.logsetup()

    def logsetup(self):
        self.logger = ialogger.IscsiAdminLogger.getlogger()
        level = ialogger.L_DEBUG
        self.logger.setLevel(level)

    def on_main_window_destroy(self, object=None, data=None):
        try:
            self.logger.logmsg("INFO", "Exiting iscsiadmin")
            gtk.main_quit()
        except RuntimeError, msg:
            pass
