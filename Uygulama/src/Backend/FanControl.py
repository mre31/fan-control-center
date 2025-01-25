from typing import Optional, List
import wmi
import ctypes
import sys
import time
import logging
from .AWCCWmiWrapper import AWCCWmiWrapper
from .Hardware_Detect import DetectHardware
from .FanProfile import ProfileManager, FanProfile

def is_admin():
    """Check if the program has admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class FanControl:
    def __init__(self) -> None:
        logging.info("Initializing FanControl...")
        
        # Check admin privileges
        if not is_admin():
            logging.error("Admin privileges required")
            raise Exception("Administrator privileges required. Please run as administrator.")

        # WMI bağlantısını birkaç kez deneme
        max_retries = 5  # Retry sayısını artırdık
        retry_delay = 2  # Bekleme süresini artırdık
        
        last_error = None
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting WMI connection (attempt {attempt + 1}/{max_retries})")
                wmi_service = wmi.WMI(namespace="root\\WMI")
                logging.info("WMI service connected")
                
                logging.info("Getting AWCC WMI class")
                awccClass = wmi_service.AWCCWmiMethodFunction
                logging.info("AWCC WMI class obtained")
                
                logging.info("Creating AWCC wrapper")
                self._awcc = AWCCWmiWrapper(awccClass()[0])
                logging.info("AWCC wrapper created successfully")
                break
                
            except Exception as ex:
                last_error = str(ex)
                logging.warning(f"WMI connection attempt {attempt + 1} failed: {ex}")
                time.sleep(retry_delay)
        else:
            error_msg = f"WMI Connection failed after {max_retries} attempts. Last error: {last_error}"
            logging.error(error_msg)
            raise Exception("Failed to connect to AWCC WMI service. Please ensure Alienware Command Center is running and try again.")

        try:
            # Tespit edilen fan ve sensör ID'lerini al
            logging.info("Detecting fan and sensor IDs")
            detected_pairs = self._awcc.GetFanIdsAndRelatedSensorsIds()
            logging.info(f"Detected pairs: {detected_pairs}")
            
            if len(detected_pairs) >= 2:
                # CPU ve GPU fan/sensör ID'lerini ayarla
                cpu_fan_id, cpu_sensor_ids = detected_pairs[0]
                gpu_fan_id, gpu_sensor_ids = detected_pairs[1]
                
                # Sınıf değişkenlerini güncelle
                self.CPU_FAN_ID = cpu_fan_id
                self.GPU_FAN_ID = gpu_fan_id
                self.CPU_SENSOR_ID = cpu_sensor_ids[0]
                self.GPU_SENSOR_ID = gpu_sensor_ids[0]
                
                logging.info(f"Fan/Sensor IDs set - CPU Fan: {cpu_fan_id}, GPU Fan: {gpu_fan_id}")
            else:
                raise Exception("Fan ve sensör ID'leri tespit edilemedi. Cihazınız desteklenmiyor olabilir.")
        except Exception as e:
            logging.error(f"Failed to initialize fan control: {str(e)}")
            raise

        # Fan ID'lerini al
        self._fanIds = self._getFanIds()
        if not self._fanIds:
            raise Exception("Fan IDs could not be retrieved")

        self.profile_manager = ProfileManager()

    def _getFanIds(self) -> List[int]:
        """Sistemdeki fan ID'lerini döndürür"""
        try:
            # CPU Fan'ı ilk sıraya koy
            return [self.CPU_FAN_ID, self.GPU_FAN_ID]
        except Exception as ex:
            print(f"Fan ID retrieval error: {ex}")
            return []

    def getAllFanRPM(self) -> List[Optional[int]]:
        """Tüm fanların RPM değerlerini döndürür"""
        rpms = []
        for fanId in self._fanIds:
            try:
                rpm = self._awcc.GetFanRPM(fanId)
                rpms.append(rpm if rpm and rpm > 0 else None)
            except:
                rpms.append(None)
        return rpms

    def _getFanRPM(self, fanId: int) -> Optional[int]:
        """Belirli bir fanın RPM değerini döndürür"""
        try:
            return self._awcc.GetFanRPM(fanId)
        except:
            return None

    def setFanSpeed(self, fanId: int, speed: int) -> bool:
        """Fan hızını ayarlar (0-100 arası)"""
        try:
            if speed < 0: speed = 0
            if speed > 100: speed = 100
            return self._awcc.SetFanSpeed(fanId, speed)
        except:
            return False

    def setAllFanSpeed(self, speed: int) -> bool:
        """Tüm fanların hızını ayarlar"""
        success = True
        for fanId in self._fanIds:
            if not self.setFanSpeed(fanId, speed):
                success = False
        return success

    def getSensorTemp(self, sensorId: int) -> Optional[int]:
        """Belirli bir sensörün sıcaklığını döndürür"""
        try:
            return self._awcc.GetSensorTemperature(sensorId)
        except:
            return None

    def apply_profile(self, profile_name: str) -> bool:
        """Belirtilen profili uygular"""
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            return False
            
        cpu_success = self.setFanSpeed(self.CPU_FAN_ID, profile.cpu_speed)
        gpu_success = self.setFanSpeed(self.GPU_FAN_ID, profile.gpu_speed)
        
        return cpu_success and gpu_success 

    def __del__(self):
        """Destructor - kaynakları temizle"""
        try:
            # WMI bağlantısını kapat
            if hasattr(self, '_awcc'):
                del self._awcc
        except:
            pass 