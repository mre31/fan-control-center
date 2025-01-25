from dataclasses import dataclass
from typing import Dict
import json
import os

@dataclass
class FanProfile:
    name: str
    cpu_speed: int
    gpu_speed: int

class ProfileManager:
    def __init__(self):
        self.profiles: Dict[str, FanProfile] = {
            "Silent": FanProfile("Silent", 30, 30),
            "Balanced": FanProfile("Balanced", 50, 50),
            "Performance": FanProfile("Performance", 70, 70),
            "G Mode": FanProfile("G Mode", 100, 100),
            "Custom": FanProfile("Custom", 50, 50)
        }
        self.current_profile: str = "Balanced"
        self._load_profiles()

    def add_profile(self, profile: FanProfile) -> bool:
        if profile.name in ["Silent", "Balanced", "Performance", "G Mode", "Custom"]:
            return False
        self.profiles[profile.name] = profile
        self._save_profiles()
        return True

    def remove_profile(self, name: str) -> bool:
        if name in ["Silent", "Balanced", "Performance", "G Mode", "Custom"]:
            return False
        if name in self.profiles:
            del self.profiles[name]
            self._save_profiles()
            return True
        return False

    def get_profile(self, name: str) -> FanProfile:
        return self.profiles.get(name)

    def get_all_profiles(self) -> Dict[str, FanProfile]:
        return self.profiles

    def _get_profile_path(self) -> str:
        app_data = os.getenv('APPDATA')
        if not app_data:
            app_data = os.path.expanduser('~')
        
        profile_dir = os.path.join(app_data, 'FanControl')
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
            
        return os.path.join(profile_dir, 'profiles.json')

    def _save_profiles(self) -> None:
        custom_profiles = {
            name: {"cpu_speed": p.cpu_speed, "gpu_speed": p.gpu_speed}
            for name, p in self.profiles.items()
            if name not in ["Silent", "Balanced", "Performance"]
        }
        
        try:
            with open(self._get_profile_path(), 'w', encoding='utf-8') as f:
                json.dump(custom_profiles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Profil kaydetme hatası: {e}")

    def _load_profiles(self) -> None:
        try:
            if os.path.exists(self._get_profile_path()):
                with open(self._get_profile_path(), 'r', encoding='utf-8') as f:
                    custom_profiles = json.load(f)
                    
                for name, data in custom_profiles.items():
                    self.profiles[name] = FanProfile(
                        name=name,
                        cpu_speed=data["cpu_speed"],
                        gpu_speed=data["gpu_speed"]
                    )
        except Exception as e:
            print(f"Profil yükleme hatası: {e}") 