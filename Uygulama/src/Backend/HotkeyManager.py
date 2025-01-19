import json
import os
from typing import Dict, Optional
from PySide6.QtCore import Qt

class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}
        self.last_profile = None
        self.settings_file = self._get_hotkeys_path()
        self._load_hotkeys()

    def _get_hotkeys_path(self) -> str:
        """Kısayol ayarları dosyasının yolunu döndürür"""
        app_data = os.getenv('APPDATA', os.path.expanduser('~'))
        hotkeys_dir = os.path.join(app_data, 'FanControl')
        
        if not os.path.exists(hotkeys_dir):
            os.makedirs(hotkeys_dir)
            
        return os.path.join(hotkeys_dir, 'hotkeys.json')

    def _load_hotkeys(self):
        """Kaydedilmiş kısayolları ve son profili yükle"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.hotkeys = data.get('hotkeys', {})
                    self.last_profile = data.get('last_profile')
        except Exception as e:
            print(f"Failed to load hotkeys: {e}")

    def _save_hotkeys(self):
        """Kısayolları ve son profili kaydet"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            data = {
                'hotkeys': self.hotkeys,
                'last_profile': self.last_profile
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save hotkeys: {e}")

    def set_hotkey(self, profile: str, hotkey: str) -> None:
        """Kısayol ata ve kaydet"""
        self.hotkeys[profile] = hotkey
        self._save_hotkeys()

    def remove_hotkey(self, profile: str) -> None:
        """Kısayolu kaldır ve kaydet"""
        if profile in self.hotkeys:
            del self.hotkeys[profile]
            self._save_hotkeys()
    
    def get_hotkey(self, profile_name: str) -> Optional[str]:
        """Profil için atanmış kısayolu döndürür"""
        return self.hotkeys.get(profile_name)
    
    def get_profile_by_key(self, key_sequence: str) -> Optional[str]:
        """Kısayola atanmış profili döndürür"""
        for profile, hotkey in self.hotkeys.items():
            if hotkey == key_sequence:
                return profile
        return None 

    def set_last_profile(self, profile: str):
        """Son kullanılan profili kaydet"""
        self.last_profile = profile
        self._save_hotkeys()

    def get_last_profile(self) -> Optional[str]:
        """Son kullanılan profili döndür"""
        return self.last_profile 

    def initialize_default_hotkeys(self):
        """Sadece ilk kurulumda varsayılan kısayolları ayarla"""
        if not os.path.exists(self.settings_file):
            self.set_hotkey("G Mode", "F17") 