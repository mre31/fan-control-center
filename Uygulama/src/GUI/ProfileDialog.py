from PySide6 import QtWidgets
from src.Backend.FanProfile import FanProfile

class ProfileDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, profile: FanProfile = None):
        super().__init__(parent)
        self.setWindowTitle("Profil Ayarları")
        self.setModal(True)
        
        layout = QtWidgets.QFormLayout(self)
        
        # Profil adı
        self.nameEdit = QtWidgets.QLineEdit()
        if profile:
            self.nameEdit.setText(profile.name)
        layout.addRow("Profil Adı:", self.nameEdit)
        
        # CPU Fan hızı
        self.cpuSpeedSpin = QtWidgets.QSpinBox()
        self.cpuSpeedSpin.setRange(0, 100)
        self.cpuSpeedSpin.setSuffix("%")
        if profile:
            self.cpuSpeedSpin.setValue(profile.cpu_speed)
        layout.addRow("CPU Fan Hızı:", self.cpuSpeedSpin)
        
        # GPU Fan hızı
        self.gpuSpeedSpin = QtWidgets.QSpinBox()
        self.gpuSpeedSpin.setRange(0, 100)
        self.gpuSpeedSpin.setSuffix("%")
        if profile:
            self.gpuSpeedSpin.setValue(profile.gpu_speed)
        layout.addRow("GPU Fan Hızı:", self.gpuSpeedSpin)
        
        # Butonlar
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addRow(buttonBox)
        
    def getProfile(self) -> FanProfile:
        return FanProfile(
            name=self.nameEdit.text(),
            cpu_speed=self.cpuSpeedSpin.value(),
            gpu_speed=self.gpuSpeedSpin.value()
        ) 