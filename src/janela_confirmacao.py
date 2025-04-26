from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont

class JanelaConfirmacao(QDialog):
    confirmado = Signal()
    cancelado  = Signal()

    def __init__(self, texto, parent=None, info_text=None):
        super().__init__(parent)

        self.info_text = info_text

        self.setWindowTitle("Informação" if info_text else "Confirmar Ação")
        self.setModal(True)
        self.resize(400, 180)
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowSystemMenuHint |
            Qt.WindowTitleHint
        )

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                color: #3D6D43;
                font-weight: bold;
            }
            QPushButton {
                padding: 10px;
                background-color: #3D6D43;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin: 0 10px;
            }
            QPushButton:hover {
                background-color: #72A06E;
            }
            QPushButton:pressed {
                background-color: #2F4F28;
            }
        """)

        self.label = QLabel(info_text if info_text else texto)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(20)
        layout.addWidget(self.label)

        h = QHBoxLayout()
        h.addStretch(1)

        if info_text:
            self.btn_ok = QPushButton("OK")
            self.btn_ok.clicked.connect(self.close)
            h.addWidget(self.btn_ok)
        else:
            self.btn_nao = QPushButton("❌ Não")
            self.btn_nao.clicked.connect(self._on_nao)
            h.addWidget(self.btn_nao)

            self.btn_sim = QPushButton("✅ Sim")
            self.btn_sim.clicked.connect(self._on_sim)
            h.addWidget(self.btn_sim)

        h.addStretch(1)
        layout.addLayout(h)

        if parent:
            pr = parent.frameGeometry()
            sr = self.frameGeometry()
            sr.moveCenter(pr.center())
            self.move(sr.topLeft())

    def _on_nao(self):
        self.cancelado.emit()
        self.close()

    def _on_sim(self):
        self.confirmado.emit()
        self.close()