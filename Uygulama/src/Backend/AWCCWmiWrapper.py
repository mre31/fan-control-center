from typing import Optional

class AWCCWmiWrapper:
    FAN_ID_FIRST = 0x32
    FAN_ID_LAST = 0x34

    def __init__(self, awcc) -> None:
        self._awcc = awcc

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
            # Sensör ID'si geçerli mi kontrol et
            if sensorId not in [0x01, 0x06]:  # Sadece CPU ve GPU sensörleri
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