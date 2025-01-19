import sys
from PySide6 import QtWidgets, QtCore
from src.GUI.AppGUI import FanControlGUI
from src.GUI.LoaderDialog import LoaderDialog
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS

def main():
    # Don't start new instance if program is already running
    mutex = CreateMutex(None, False, "FanControlCenter_Mutex")
    if GetLastError() == ERROR_ALREADY_EXISTS:
        CloseHandle(mutex)
        return
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Check for minimize parameter
    start_minimized = "--minimized" in sys.argv
    
    # Show loader dialog
    if not start_minimized:
        loader = LoaderDialog()
        loader.show()
        app.processEvents()
    
    window = FanControlGUI()
    
    if not start_minimized:
        loader.close()
    
    if start_minimized:
        # Sistem tepsisinde başlat
        window.hide()
        # Bildirim gösterimini engelle
        window._suppressNotification = True
    else:
        window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 