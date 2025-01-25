from typing import Callable, Optional
from PySide6 import QtCore, QtWidgets
from .QGauge import QGauge
from .AppColors import Colors

class ThermalUnitWidget(QtWidgets.QGroupBox):
    def __init__(self, title: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)
        
        # Ana layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Sıcaklık göstergesi
        self._tempGauge = QGauge()
        self._tempGauge.setMaximum(100)  # Maksimum 100°C
        self._tempGauge.setColorScheme({
            0: Colors.GREEN.value,    # 0-59°C arası yeşil
            60: Colors.YELLOW.value,  # 60-84°C arası sarı
            85: Colors.RED.value      # 85°C ve üstü kırmızı
        })
        layout.addWidget(self._tempGauge)
        
        # RPM Göstergesi - Sabit mavi renk
        self._rpmGauge = QGauge()
        self._rpmGauge.setMaximum(5000)  # Maksimum 5000 RPM
        self._rpmGauge.setColorScheme({
            0: Colors.BLUE.value  # Tüm değerler için mavi
        })
        layout.addWidget(self._rpmGauge)
        
        # Hız kontrolü slider
        sliderLayout = QtWidgets.QHBoxLayout()
        self._speedSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._speedSlider.setRange(0, 100)
        self._speedLabel = QtWidgets.QLabel("0%")
        
        sliderLayout.addWidget(self._speedSlider)
        sliderLayout.addWidget(self._speedLabel)
        layout.addLayout(sliderLayout)
        
        # Slider değişikliklerini izle
        self._speedSlider.valueChanged.connect(self._onSpeedChanged)
        
        # Callback fonksiyonları
        self._speedChangeCallback: Optional[Callable[[int], None]] = None
        
    def setSpeedChangeCallback(self, callback: Callable[[int], None]) -> None:
        """Fan hızı değiştiğinde çağrılacak fonksiyonu ayarla"""
        self._speedChangeCallback = callback
        
    def updateRPM(self, rpm: Optional[int]) -> None:
        """RPM değerini güncelle"""
        if rpm is None:
            self._rpmGauge.setValue(0)
            self._rpmGauge.setFormat("0 RPM")  # N/A yerine 0 RPM göster
        else:
            self._rpmGauge.setValue(min(5000, rpm))  # 5000 RPM maksimum
            self._rpmGauge.setFormat(f"{rpm} RPM")
            
    def updateTemp(self, temp: Optional[int]) -> None:
        """Sıcaklık değerini güncelle"""
        if temp is None:
            self._tempGauge.setValue(0)
            self._tempGauge.setFormat("N/A")
        else:
            self._tempGauge.setValue(temp)
            self._tempGauge.setFormat(f"{temp}°C")
            
    def setSpeed(self, speed: int) -> None:
        """Fan hızını ayarla (slider'ı günceller)"""
        self._speedSlider.setValue(speed)
        
    @QtCore.Slot()
    def _onSpeedChanged(self) -> None:
        """Slider değeri değiştiğinde çağrılır"""
        speed = self._speedSlider.value()
        self._speedLabel.setText(f"{speed}%")
        
        if self._speedChangeCallback:
            self._speedChangeCallback(speed) 