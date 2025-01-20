from typing import Optional, Tuple
from enum import Enum
from .Hardware_Detect import NoAWCCWMIClass, CannotInstAWCCWMI

class AWCCWmiWrapper:
    SENSOR_ID_FIRST = 0x01
    SENSOR_ID_LAST = 0x30
    FAN_ID_FIRST = 0x31
    FAN_ID_LAST = 0x63

    class ThermalMode(Enum):
        Custom = 0
        Balanced = 0x97
        G_Mode = 0xAB

    def __init__(self, awcc) -> None:
        self._awcc = awcc
        self._detected_ids = self._detect_fan_sensor_ids()

    def _detect_fan_sensor_ids(self) -> list[Tuple[int, Tuple[int, ...]]]:
        """Fan ve sensör ID'lerini tespit eder"""
        detected_pairs = []
        
        # Bilinen sensör ID'leri
        cpu_sensor_ids = [0x01, 0x02, 0x03]  # CPU sensörleri genellikle düşük ID'lerde
        gpu_sensor_ids = [0x06, 0x07, 0x08]  # GPU sensörleri genellikle yüksek ID'lerde
        
        # Önce çalışan fanları bul
        working_fans = []
        for fan_id in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1):
            rpm = self.GetFanRPM(fan_id)
            if rpm is not None and rpm > 0:
                working_fans.append(fan_id)
        
        if len(working_fans) < 2:
            raise Exception("Could not detect at least 2 working fans")
            
        # CPU Fan ve Sensör eşleştirmesi
        for fan_id in working_fans:
            # CPU sensörlerini kontrol et
            for sensor_id in cpu_sensor_ids:
                temp = self.GetSensorTemperature(sensor_id)
                if temp is not None and 20 <= temp <= 100:
                    detected_pairs.append((fan_id, (sensor_id,)))
                    working_fans.remove(fan_id)
                    break
            if len(detected_pairs) == 1:  # CPU fan/sensör bulundu
                break
                
        # GPU Fan ve Sensör eşleştirmesi
        if working_fans and len(detected_pairs) == 1:
            for fan_id in working_fans:
                # GPU sensörlerini kontrol et
                for sensor_id in gpu_sensor_ids:
                    temp = self.GetSensorTemperature(sensor_id)
                    if temp is not None and 20 <= temp <= 100:
                        detected_pairs.append((fan_id, (sensor_id,)))
                        break
                if len(detected_pairs) == 2:  # GPU fan/sensör bulundu
                    break
        
        if len(detected_pairs) < 2:
            raise Exception("Fan and sensor IDs could not be detected. Your device might not be supported.")
            
        return detected_pairs

    def GetFanIdsAndRelatedSensorsIds(self) -> list[Tuple[int, Tuple[int, ...]]]:
        """Tespit edilen fan ve sensör ID'lerini döndürür"""
        return self._detected_ids

    def GetFanRPM(self, fanId: int) -> Optional[int]:
        """Fan RPM değerini al"""
        if not (fanId in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1)):
            return None
        try:
            arg = ((fanId & 0xFF) << 8) | 0x05
            val = self._call('Thermal_Information', arg)
            if val and val > 0:
                return val
            return None
        except Exception as e:
            return None

    def SetFanSpeed(self, fanId: int, speed: int) -> bool:
        """Fan hızını ayarla"""
        if not (fanId in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1)):
            return False
        if speed > 0xFF: speed = 0xFF
        try:
            arg = ((speed & 0xFF) << 16) | ((fanId & 0xFF) << 8) | 2
            return self._call('Thermal_Control', arg) == 0
        except:
            return False

    def GetSensorTemperature(self, sensorId: int) -> Optional[int]:
        """Sensör sıcaklığını al"""
        try:
            # Sensör ID'si geçerli aralıkta mı kontrol et
            if not (sensorId in range(self.SENSOR_ID_FIRST, self.SENSOR_ID_LAST + 1)):
                return None

            # Sıcaklık okuma argümanını hazırla
            arg = ((sensorId & 0xFF) << 8) | 4

            val = self._call('Thermal_Information', arg)
            
            # Sıcaklık değeri geçerli mi kontrol et
            if val and isinstance(val, int) and 0 < val < 125:
                return val
            return None
        except Exception as e:
            return None

    def _call(self, method: str, arg: int) -> Optional[int]:
        """WMI metodunu çağır"""
        try:
            val = self._awcc.Thermal_Information(arg) if method == 'Thermal_Information' else \
                  self._awcc.Thermal_Control(arg) if method == 'Thermal_Control' else None
                  
            if isinstance(val, tuple):
                val = val[0]
            if not isinstance(val, int) or val == -1 or val == 0xFFFFFFFF:
                return None
            return val
        except:
            return None 