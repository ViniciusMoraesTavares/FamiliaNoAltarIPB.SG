# src/janela_confirmacao.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont

class JanelaConfirmacao(QDialog):
    confirmado = Signal()
    cancelado  = Signal()

    def __init__(self, texto, parent=None, info_text=None):
        super().__init__(parent)

        self.info_text = info_text   # texto de sucesso (pode ser None)

        # decoração e modal
        self.setWindowTitle("Informação" if info_text else "Confirmar Ação")
        self.setModal(True)
        self.resize(400, 180)
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowSystemMenuHint |
            Qt.WindowTitleHint
        )

        # mesmo styleSheet das suas janelas
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

        # === widget de mensagem ===
        self.label = QLabel(info_text if info_text else texto)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        # layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(20)
        layout.addWidget(self.label)

        h = QHBoxLayout()
        h.addStretch(1)

        if info_text:
            # Se tiver info_text, mostra apenas o botão OK
            self.btn_ok = QPushButton("OK")
            self.btn_ok.clicked.connect(self.close)
            h.addWidget(self.btn_ok)
        else:
            # Se não tiver info_text, mostra os botões Sim e Não
            self.btn_nao = QPushButton("❌ Não")
            self.btn_nao.clicked.connect(self._on_nao)
            h.addWidget(self.btn_nao)

            self.btn_sim = QPushButton("✅ Sim")
            self.btn_sim.clicked.connect(self._on_sim)
            h.addWidget(self.btn_sim)

        h.addStretch(1)
        layout.addLayout(h)

        # centralizar sobre o parent
        if parent:
            pr = parent.frameGeometry()
            sr = self.frameGeometry()
            sr.moveCenter(pr.center())
            self.move(sr.topLeft())

    def _on_nao(self):
        # usuário cancelou
        self.cancelado.emit()
        self.close()

    def _on_sim(self):
        # dispara o sinal para exclusão
        self.confirmado.emit()
        self.close()
