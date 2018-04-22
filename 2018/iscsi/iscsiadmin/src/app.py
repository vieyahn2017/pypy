import sys
from iscsiadmin import IscsiadminApp
try:
    import gtk
except:
    print("An error occurred while importing gtk")
    print("Please make sure you have a valid GTK+ Runtime Environment.")
    sys.exit(1)


def main():
    try:
        MainApp = IscsiadminApp()
        gtk.main()
    except KeyboardInterrupt:
        MainApp.on_main_window_destroy()

if __name__ == "__main__":
    main()
