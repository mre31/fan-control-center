import keyboard
from typing import Dict, Callable
import queue
import atexit
import threading

class GlobalHotkey:
    def __init__(self):
        self._hotkeys = {}
        self.running = True
        self.message_queue = queue.Queue()
        self.worker_thread = None
        
        # Program kapanırken temizlik yap
        atexit.register(self.cleanup)
        
    def _process_queue(self):
        """Mesaj kuyruğunu işleyen thread fonksiyonu"""
        while self.running:
            try:
                # Kuyruktaki callback'i al ve çalıştır
                callback = self.message_queue.get(timeout=0.1)
                if callback:
                    callback()
            except queue.Empty:
                continue
            except Exception:
                pass
                
    def register(self, key_sequence: str, callback: Callable) -> bool:
        try:
            hotkey = key_sequence.replace('+', '+').lower()
            keyboard.add_hotkey(hotkey, lambda: self.message_queue.put(callback))
            self._hotkeys[key_sequence] = callback
            return True
        except:
            return False

    def unregister(self, key_sequence: str) -> bool:
        try:
            if key_sequence in self._hotkeys:
                hotkey = key_sequence.replace('+', '+').lower()
                keyboard.remove_hotkey(hotkey)
                del self._hotkeys[key_sequence]
                return True
            return False
        except:
            return False

    def start(self):
        self.running = True
        # Message queue işleme thread'ini başlat
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Tüm kısayolları devre dışı bırak"""
        self.running = False
        # Worker thread'in durmasını bekle
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        # Tüm kısayolları temizle
        for key in list(self._hotkeys.keys()):
            self.unregister(key)

    def cleanup(self):
        try:
            self.stop()
            keyboard.unhook_all()
            self._hotkeys.clear()
        except:
            pass 