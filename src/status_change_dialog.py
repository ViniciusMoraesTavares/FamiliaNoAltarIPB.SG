from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame
from PySide6.QtGui import QIcon
import os, sys
from src.icon import get_icon_path

class StatusChangeDialog(QDialog):
    confirmado = Signal()
    cancelado  = Signal()

    def __init__(self, texto, impactos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alterar Status da Família")
        self.setModal(True)
        self.resize(480, 240)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        try:
            icon_path = get_icon_path()
            if icon_path:
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; border-radius: 8px; }
            QLabel#title { font-size: 18px; color: #1F2937; font-weight: 700; }
            QLabel { font-size: 14px; color: #374151; }
            QFrame#box { border: 1px solid #E5E7EB; border-radius: 8px; background: #FAFAFA; }
            QPushButton#cancelar {
                padding: 10px 16px; background-color: #FFFFFF; color: #374151;
                border: 1px solid #D1D5DB; border-radius: 8px; font-size: 14px; font-weight: 600;
            }
            QPushButton#cancelar:hover { background-color: #F3F4F6; }
            QPushButton#confirmar {
                padding: 10px 16px; background-color: #2E7D32; color: #FFFFFF;
                border: none; border-radius: 8px; font-size: 14px; font-weight: 700;
            }
            QPushButton#confirmar:hover { background-color: #1B5E20; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Confirmar alteração de status")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        msg = QLabel(texto)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        box = QFrame()
        box.setObjectName("box")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(12, 12, 12, 12)
        for line in impactos:
            lbl = QLabel(f"• {line}")
            bl.addWidget(lbl)
        layout.addWidget(box)

        h = QHBoxLayout()
        h.addStretch(1)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.clicked.connect(self._on_cancelar)
        h.addWidget(btn_cancelar)
        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.setObjectName("confirmar")
        btn_confirmar.clicked.connect(self._on_confirmar)
        h.addWidget(btn_confirmar)
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

    def _on_confirmar(self):
        self.confirmado.emit()
        self.close()
