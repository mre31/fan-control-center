import keyboard
from typing import Dict, Callable
import queue
import atexit
import threading

class GlobalHotkey:
    def __init__(self):
        self.running = True
        self.hotkeys: Dict[str, Callable] = {}
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
            except Exception as e:
                print(f"Error processing hotkey callback: {e}")
                
    def register(self, key_sequence: str, callback: Callable) -> bool:
        try:
            # Tuş kombinasyonunu keyboard kütüphanesi formatına çevir
            hotkey = key_sequence.replace('+', '+').lower()
            
            # Kısayolu kaydet
            keyboard.add_hotkey(hotkey, lambda: self.message_queue.put(callback))
            self.hotkeys[key_sequence] = callback
            return True
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False

    def unregister(self, key_sequence: str) -> bool:
        try:
            if key_sequence in self.hotkeys:
                # Tuş kombinasyonunu keyboard kütüphanesi formatına çevir
                hotkey = key_sequence.replace('+', '+').lower()
                keyboard.remove_hotkey(hotkey)
                del self.hotkeys[key_sequence]
                return True
            return False
        except Exception as e:
            print(f"Failed to unregister hotkey: {e}")
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
        for key_sequence in list(self.hotkeys.keys()):
            self.unregister(key_sequence)

    def cleanup(self):
        """Tüm kaynakları temizle"""
        try:
            # Önce tüm kısayolları devre dışı bırak
            self.stop()
            
            # keyboard hook'larını temizle
            keyboard.unhook_all()
            
            # Event listener'ları durdur
            keyboard._listener.stop_if_exists()
            
            # Kuyrukları temizle
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except queue.Empty:
                    break
                    
            # Referansları temizle
            self.hotkeys.clear()
            
        except Exception as e:
            print(f"Error during GlobalHotkey cleanup: {e}") 