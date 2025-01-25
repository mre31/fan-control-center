from typing import Optional, Tuple
from enum import Enum
from .Hardware_Detect import NoAWCCWMIClass, CannotInstAWCCWMI
import time

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
        try:
            detected_pairs = []
            known_pairs = [
                (0x32, 0x01),  # CPU Fan ve Sensör
                (0x33, 0x06)   # GPU Fan ve Sensör
            ]
            
            for fan_id, sensor_id in known_pairs:
                rpm = self.GetFanRPM(fan_id)
                if rpm is not None:
                    temp = self.GetSensorTemperature(sensor_id)
                    if temp is not None:
                        detected_pairs.append((fan_id, (sensor_id,)))
            
            if not detected_pairs:
                working_fans = []
                for fan_id in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1):
                    rpm = self.GetFanRPM(fan_id)
                    if rpm is not None:
                        working_fans.append(fan_id)
            
            if not detected_pairs:
                detected_pairs = [(0x32, (0x01,)), (0x33, (0x06,))]
            
            return detected_pairs
            
        except Exception:
            return [(0x32, (0x01,)), (0x33, (0x06,))]

    def GetFanIdsAndRelatedSensorsIds(self) -> list[Tuple[int, Tuple[int, ...]]]:
        """Tespit edilen fan ve sensör ID'lerini döndürür"""
        return self._detected_ids

    def GetFanRPM(self, fanId: int) -> Optional[int]:
        try:
            if not (fanId in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1)):
                return None
            
            time.sleep(0.05)
            arg = ((fanId & 0xFF) << 8) | 0x05
            val = self._call('Thermal_Information', arg)
            
            if val is not None and isinstance(val, int):
                if val == -1 or val == 0xFFFFFFFF:
                    return None
                if 0 <= val <= 20000:
                    return val
            return None
            
        except Exception:
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
            if not (sensorId in range(self.SENSOR_ID_FIRST, self.SENSOR_ID_LAST + 1)):
                return None
            
            # WMI çağrısı öncesi kısa bekleme
            time.sleep(0.05)
            
            # Sıcaklık bilgisini al
            arg = ((sensorId & 0xFF) << 8) | 4
            val = self._call('Thermal_Information', arg)
            
            # Değeri doğrula
            if val is not None and isinstance(val, int):
                if val == -1 or val == 0xFFFFFFFF:
                    return None
                if 0 <= val <= 125:  # Makul sıcaklık aralığı
                    return val
            return None
            
        except Exception:
            return None

    def _call(self, method: str, arg: int) -> Optional[int]:
        try:
            time.sleep(0.05)
            
            if method == 'Thermal_Information':
                val = self._awcc.Thermal_Information(arg)
            elif method == 'Thermal_Control':
                val = self._awcc.Thermal_Control(arg)
            else:
                return None
            
            if isinstance(val, tuple):
                val = val[0]
            
            if not isinstance(val, int):
                return None
            
            return val
            
        except Exception:
            return None 