from enum import Enum
from typing import Optional, Tuple, Union, NewType
import wmi
import time

# DetectHardware class
class DetectHardware:
    CPUFanIdx = 0
    GPUFanIdx = 1

    def __init__(self) -> None:
        self._wmi = wmi.WMI()

    def getHardwareName(self, fanIdx: int) -> Optional[str]:
        try:
            if fanIdx == self.CPUFanIdx:
                # CPU bilgisini al
                cpu = self._wmi.Win32_Processor()[0]
                return cpu.Name.strip() if hasattr(cpu, 'Name') else None
            
            elif fanIdx == self.GPUFanIdx:
                # Sadece NVIDIA veya AMD GPU'ları al
                gpus = [gpu for gpu in self._wmi.Win32_VideoController() 
                       if any(vendor in gpu.Name for vendor in ['NVIDIA', 'AMD', 'Radeon'])
                       if hasattr(gpu, 'Name')]
                
                if gpus:
                    # En yüksek VRAM'e sahip GPU'yu seç
                    dedicated_gpu = max(gpus, 
                        key=lambda gpu: getattr(gpu, 'AdapterRAM', 0) 
                        if hasattr(gpu, 'AdapterRAM') else 0)
                    return dedicated_gpu.Name.strip()
                return None
            
            return None
            
        except Exception as e:
            print(f"Error getting hardware name: {e}")
            return None

# Required classes for AWCC
class NoAWCCWMIClass(Exception):
    def __init__(self) -> None:
        super().__init__("AWCC WMI class not found in the system")

class CannotInstAWCCWMI(Exception):
    def __init__(self) -> None:
        super().__init__("Couldn't instantiate AWCC WMI class")

class AWCCWmiWrapper:
    SENSOR_ID_FIRST = 0x01
    SENSOR_ID_LAST = 0x30
    FAN_ID_FIRST = 0x31
    FAN_ID_LAST = 0x63

    class ThermalMode(Enum):
        Custom = 0
        Balanced = 0x97
        G_Mode = 0xAB

    def __init__(self, awcc: wmi._wmi_object) -> None:
        self._awcc = awcc
        self._detected_ids = self._detect_fan_sensor_ids()

    def _detect_fan_sensor_ids(self) -> list[Tuple[int, Tuple[int, ...]]]:
        """Fan ve sensör ID'lerini tespit eder"""
        detected_pairs = []
        
        # CPU Fan ve Sensör tespiti
        for fan_id in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1):
            # Fan RPM'ini kontrol et
            rpm = self.GetFanRPM(fan_id)
            if rpm is not None and rpm > 0:
                # İlgili sensörü bul
                for sensor_id in range(self.SENSOR_ID_FIRST, self.SENSOR_ID_LAST + 1):
                    temp = self.GetSensorTemperature(sensor_id)
                    if temp is not None and 20 <= temp <= 100:  # Makul sıcaklık aralığı
                        detected_pairs.append((fan_id, (sensor_id,)))
                        break
        
        # En az 2 fan/sensör çifti bulunamazsa varsayılan değerleri kullan
        if len(detected_pairs) < 2:
            return [(0x33, (1,)), (0x32, (6,))]  # Varsayılan değerler
            
        # CPU ve GPU fan/sensör çiftlerini sırala
        # CPU genellikle daha düşük ID'ye sahiptir
        detected_pairs.sort(key=lambda x: x[0])
        return detected_pairs

    def GetFanIdsAndRelatedSensorsIds(self) -> list[Tuple[int, Tuple[int, ...]]]:
        return self._detected_ids

    def GetFanRPM(self, fanId: int) -> Optional[int]:
        if not (fanId in range(self.FAN_ID_FIRST, self.FAN_ID_LAST + 1)): return None
        arg = ((fanId & 0xFF) << 8) | 5
        return self._call('Thermal_Information', arg)

    def GetSensorTemperature(self, sensorId: int) -> Optional[int]:
        if not (sensorId in range(self.SENSOR_ID_FIRST, self.SENSOR_ID_LAST + 1)): return None
        arg = ((sensorId & 0xFF) << 8) | 4
        return self._call('Thermal_Information', arg)

    def _call(self, method: str, arg: int) -> Optional[int]:
        if not hasattr(self._awcc, method) or not callable(getattr(self._awcc, method)):
            return None
        val: int = getattr(self._awcc, method)(arg)[0]
        if not isinstance(val, int) or val == -1 or val == 0xFFFFFFFF: 
            return None
        return val

class AWCCThermal:
    Mode = AWCCWmiWrapper.ThermalMode
    ModeType = NewType("ModeType", AWCCWmiWrapper.ThermalMode)
    CPUFanIdx = 0
    GPUFanIdx = 1

    def __init__(self, awcc: Optional[AWCCWmiWrapper] = None) -> None:
        if awcc is None:
            try:
                awccClass = wmi.WMI(namespace="root\\WMI").AWCCWmiMethodFunction
            except Exception as ex:
                print(ex)
                raise NoAWCCWMIClass()
            try:
                awcc = AWCCWmiWrapper(awccClass()[0])
            except Exception as ex:
                print(ex)
                raise CannotInstAWCCWMI()
        self._awcc = awcc
        self._fanIdsAndRelatedSensorsIds = self._awcc.GetFanIdsAndRelatedSensorsIds()
        self._fanIds = [id for id, _ in self._fanIdsAndRelatedSensorsIds]

    def getAllFanRPM(self) -> list[Optional[int]]:
        return [self._awcc.GetFanRPM(fanId) for fanId in self._fanIds]

    def getAllTemp(self) -> list[Optional[int]]:
        return [self._awcc.GetSensorTemperature(sensorId) for _, ids in self._fanIdsAndRelatedSensorsIds for sensorId in ids]

def main():
    try:
        # Initialize hardware detection
        hw_detect = DetectHardware()
        thermal = AWCCThermal()
        
        print("Hardware Information:")
        print("-" * 50)
        
        # Get CPU and GPU names
        cpu_name = hw_detect.getHardwareName(DetectHardware.CPUFanIdx)
        gpu_name = hw_detect.getHardwareName(DetectHardware.GPUFanIdx)
        
        # Get Fan and Sensor IDs
        fan_sensor_ids = thermal._fanIdsAndRelatedSensorsIds
        cpu_fan_id, cpu_sensor_ids = fan_sensor_ids[0]
        gpu_fan_id, gpu_sensor_ids = fan_sensor_ids[1]
        
        print(f"CPU: {cpu_name}")
        print(f"CPU Fan ID: 0x{cpu_fan_id:02X}, Sensor ID: 0x{cpu_sensor_ids[0]:02X}")
        print(f"GPU: {gpu_name}")
        print(f"GPU Fan ID: 0x{gpu_fan_id:02X}, Sensor ID: 0x{gpu_sensor_ids[0]:02X}")
        print("-" * 50)
        
        # Continuously read fan RPM and temperature values
        print("Hardware Values (Press Ctrl+C to exit):")
        while True:
            fan_rpms = thermal.getAllFanRPM()
            temperatures = thermal.getAllTemp()
            
            if len(fan_rpms) >= 2 and len(temperatures) >= 2:
                status = (
                    f"\rCPU [FAN 0x{cpu_fan_id:02X}|SENS 0x{cpu_sensor_ids[0]:02X}]: "
                    f"{temperatures[0]}°C ({fan_rpms[0]} RPM) | "
                    f"GPU [FAN 0x{gpu_fan_id:02X}|SENS 0x{gpu_sensor_ids[0]:02X}]: "
                    f"{temperatures[1]}°C ({fan_rpms[1]} RPM)"
                )
                print(status, end="", flush=True)
            else:
                print("\rCould not read values", end="", flush=True)
                
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nProgram terminated.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 