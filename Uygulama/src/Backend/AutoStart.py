import os
import sys
import subprocess

class AutoStart:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.task_name = "FanControlCenter"
        
    def enable(self) -> bool:
        """Enable autostart with Task Scheduler"""
        try:
            # Get application path
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = os.path.abspath(sys.argv[0])
            
            # XML içeriği oluştur
            xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Fan Control Center Auto Start</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{app_path}"</Command>
      <Arguments>--minimized</Arguments>
    </Exec>
  </Actions>
</Task>"""
            
            # Geçici XML dosyası oluştur
            xml_path = os.path.join(os.environ['TEMP'], 'fan_control_task.xml')
            with open(xml_path, 'w', encoding='utf-16') as f:
                f.write(xml_content)
            
            # Task Scheduler'a görevi ekle
            subprocess.run([
                'schtasks', 
                '/create', 
                '/tn', self.task_name,
                '/xml', xml_path,
                '/f'  # Varsa üzerine yaz
            ], check=True)
            
            # Geçici dosyayı sil
            os.remove(xml_path)
            return True
            
        except Exception as e:
            print(f"Failed to enable autostart: {e}")
            return False

    def disable(self) -> bool:
        """Disable autostart"""
        try:
            subprocess.run([
                'schtasks', 
                '/delete', 
                '/tn', self.task_name,
                '/f'
            ], check=True)
            return True
        except Exception as e:
            print(f"Failed to disable autostart: {e}")
            return False
            
    def is_enabled(self) -> bool:
        """Check if autostart is enabled"""
        try:
            result = subprocess.run([
                'schtasks', 
                '/query', 
                '/tn', self.task_name
            ], capture_output=True)
            return result.returncode == 0
        except:
            return False 