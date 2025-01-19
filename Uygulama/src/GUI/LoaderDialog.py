from PySide6 import QtWidgets, QtCore, QtGui

class LoaderDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setModal(True)
        
        # Pencere boyutunu ayarla
        self.setFixedSize(900, 400)  # Ana pencere ile aynı boyut
        
        # Ekranın ortasına konumlandır
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - 900) // 2
        y = (screen.height() - 400) // 2
        self.move(x, y)
        
        # Yarı saydam siyah arka plan
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(32, 32, 32, 0.95);
                border-radius: 10px;  /* Köşeleri yuvarla */
            }
            QLabel {
                color: #DDDDDD;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        
        # Ana layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # İçerik için container
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Loading animasyonu
        self.spinner = QtWidgets.QLabel()
        self.spinner.setAlignment(QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.spinner)
        
        # Loading metni
        self.text = QtWidgets.QLabel("Loading...")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        container_layout.addWidget(self.text)
        
        # Container'ı ana layout'a ekle
        layout.addWidget(container)
        
        # Animasyon için timer
        self.angle = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(30)
    
    def _rotate(self):
        self.angle = (self.angle + 10) % 360
        svg = f'''
            <svg width="60" height="60" viewBox="0 0 60 60">
                <circle cx="30" cy="30" r="25" fill="none" 
                        stroke="#3498db" stroke-width="5" 
                        stroke-dasharray="90, 150" 
                        transform="rotate({self.angle} 30 30)"/>
            </svg>
        '''
        self.spinner.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(svg.encode(), 'SVG'))) 