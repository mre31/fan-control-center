import sys
from PySide6 import QtWidgets, QtCore
from src.GUI.AppGUI import FanControlGUI
from src.GUI.LoaderDialog import LoaderDialog
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS

def main():
    try:
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
        
    except Exception as e:
        # Hata mesajını bir dosyaya kaydet
        import traceback
        from datetime import datetime
        import os
        
        app_data = os.getenv('APPDATA', os.path.expanduser('~'))
        log_dir = os.path.join(app_data, 'FanControl', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Error occurred at: {datetime.now()}\n")
            f.write(f"Error message: {str(e)}\n")
            f.write("\nTraceback:\n")
            f.write(traceback.format_exc())
        
        # Hata mesajını göster
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, 
            f"An error occurred: {str(e)}\n\nCheck the log file at:\n{log_file}", 
            "Fan Control Center Error", 
            0x10)
        sys.exit(1)

if __name__ == "__main__":
    main() 