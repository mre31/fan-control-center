from PySide6 import QtWidgets, QtCore, QtGui

class HotkeyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Hotkey")
        self.setModal(True)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Bilgi etiketi
        label = QtWidgets.QLabel("Press any key or key combination...")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        
        self.key_sequence = None
        
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
            return
            
        key = event.key()
        modifiers = event.modifiers()
        
        # Tuş kombinasyonunu oluştur
        sequence = []
        
        # Modifier tuşları varsa ekle
        if modifiers & QtCore.Qt.ControlModifier:
            sequence.append("Ctrl")
        if modifiers & QtCore.Qt.AltModifier:
            sequence.append("Alt")
        if modifiers & QtCore.Qt.ShiftModifier:
            sequence.append("Shift")
            
        # Ana tuşu ekle
        key_text = QtGui.QKeySequence(key).toString()
        if key_text and key not in [QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Shift]:
            sequence.append(key_text)
            # Tuş kombinasyonunu kaydet
            self.key_sequence = "+".join(sequence)
            self.accept() 