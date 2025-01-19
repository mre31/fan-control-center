from typing import Optional, Dict
from PySide6 import QtWidgets, QtCore
from .AppColors import Colors

class QGauge(QtWidgets.QProgressBar):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName('QGauge')
        self._colorScheme: Dict[int, str] = {
            0: Colors.GREEN.value,     # Default color scheme
            50: Colors.YELLOW.value,
            75: Colors.RED.value
        }
        self._label: Optional[QtWidgets.QLabel] = None
        
        # Default style
        self.setTextVisible(True)
        self.setMinimum(0)
        self.setMaximum(100)
        
        # Set initial color
        self._updateColor()
        self.valueChanged.connect(self._updateColor)

    def setColorScheme(self, colorScheme: Dict[int, str]) -> None:
        """Renk şemasını ayarla"""
        if not colorScheme:  # Boş şema kontrolü
            return
        self._colorScheme = colorScheme
        self._updateColor()

    def createLabel(self) -> QtWidgets.QLabel:
        """Gösterge için harici etiket oluştur"""
        if not self._label:
            self._label = QtWidgets.QLabel()
            self.valueChanged.connect(self._updateLabel)
        return self._label

    def setValue(self, value: int) -> None:
        """Değeri güvenli bir şekilde ayarla"""
        value = max(self.minimum(), min(self.maximum(), value))
        super().setValue(value)

    @QtCore.Slot()
    def _updateColor(self) -> None:
        """Değere göre rengi güncelle"""
        if not self._colorScheme:
            return
            
        try:
            value = self.value()
            thresholds = [k for k in self._colorScheme.keys() if k <= value]
            if thresholds:  # Liste boş değilse
                background_color = self._colorScheme[max(thresholds)]
                
                # Arka plan renginin parlaklığını hesapla
                # Hex renk kodunu RGB'ye çevir
                r = int(background_color[1:3], 16)
                g = int(background_color[3:5], 16)
                b = int(background_color[5:7], 16)
                
                # Parlaklık formülü (0-255 arası)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                
                # Parlaklığa göre metin rengini seç (koyu/açık)
                text_color = "#000000" if brightness > 128 else "#FFFFFF"
                
                self.setStyleSheet(f"""
                    QProgressBar {{
                        border: 2px solid {Colors.GREY.value};
                        border-radius: 5px;
                        text-align: center;
                        background-color: {Colors.DARK_GREY.value};
                        color: {text_color};  /* Metin rengi */
                    }}
                    QProgressBar::chunk {{
                        background-color: {background_color};
                        border-radius: 3px;
                    }}
                """)
        except Exception as e:
            print(f"Renk güncelleme hatası: {e}")

    @QtCore.Slot()
    def _updateLabel(self) -> None:
        """Harici etiketi güncelle"""
        if self._label:
            self._label.setText(self.text()) 