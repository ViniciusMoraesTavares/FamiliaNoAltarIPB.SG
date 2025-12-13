from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

class DeleteConfirmDialog(QDialog):
    confirmado = Signal()
    cancelado  = Signal()

    def __init__(self, texto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Exclusão")
        self.setModal(True)
        self.resize(420, 180)
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowSystemMenuHint |
            Qt.WindowTitleHint
        )

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            QLabel#message {
                font-size: 16px;
                color: #1F2937;
                font-weight: 600;
            }
            QPushButton#cancelar {
                padding: 10px 16px;
                background-color: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#cancelar:hover {
                background-color: #F3F4F6;
            }
            QPushButton#excluir {
                padding: 10px 16px;
                background-color: #DC2626;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#excluir:hover {
                background-color: #B91C1C;
            }
        """)

        self.label = QLabel(texto)
        self.label.setObjectName("message")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        layout.addWidget(self.label)

        h = QHBoxLayout()
        h.addStretch(1)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("cancelar")
        self.btn_cancelar.clicked.connect(self._on_cancelar)
        h.addWidget(self.btn_cancelar)

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setObjectName("excluir")
        self.btn_excluir.clicked.connect(self._on_excluir)
        h.addWidget(self.btn_excluir)
        h.addStretch(1)

        layout.addLayout(h)

        if parent:
            pr = parent.frameGeometry()
            sr = self.frameGeometry()
            sr.moveCenter(pr.center())
            self.move(sr.topLeft())

    def _on_cancelar(self):
        self.cancelado.emit()
        self.close()

    def _on_excluir(self):
        self.confirmado.emit()
        self.close()
