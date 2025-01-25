import sys
from PySide6 import QtWidgets, QtCore
import os
import traceback
import ctypes
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    try:
        # Check admin rights first
        if not is_admin():
            # Re-run the program with admin rights
            if getattr(sys, 'frozen', False):
                # If it's an exe
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            else:
                # If it's a script
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"' + sys.argv[0] + '"', None, 1)
            return

        from win32event import CreateMutex
        from win32api import CloseHandle, GetLastError
        from winerror import ERROR_ALREADY_EXISTS
        from src.GUI.AppGUI import FanControlGUI
        from src.GUI.LoaderDialog import LoaderDialog
        
        mutex = CreateMutex(None, False, "FanControlCenter_Mutex")
        if GetLastError() == ERROR_ALREADY_EXISTS:
            CloseHandle(mutex)
            return
        
        app = QtWidgets.QApplication(sys.argv)
        
        start_minimized = "--minimized" in sys.argv
        
        loader = None
        if not start_minimized:
            try:
                loader = LoaderDialog()
                loader.show()
                app.processEvents()
            except Exception:
                pass
        
        try:
            window = FanControlGUI()
        except Exception as e:
            if loader:
                loader.close()
            raise
        
        if loader:
            loader.close()
        
        if start_minimized:
            window.hide()
            window._suppressNotification = True
        else:
            window.show()
        
        return app.exec()
        
    except Exception as e:
        error_msg = f"Kritik bir hata oluştu:\n\n{str(e)}"
        ctypes.windll.user32.MessageBoxW(0, error_msg, "Fan Control Center Hata", 0x10)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        sys.exit(1) 