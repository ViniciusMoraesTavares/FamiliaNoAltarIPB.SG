from PySide6.QtCore import Signal, Qt  
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QFrame
from PySide6.QtGui import QFont, QPixmap
import os
from src.data_manager import DataManager
from PySide6.QtGui import QIcon
import sys
from src.icon import get_icon_path

class JanelaAdicionarFamilia(QDialog):
    familia_adicionada = Signal()  

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adicionar Família")
        try:
            icon_path = get_icon_path()
            if icon_path:
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; border-radius: 10px; }
            QLabel#title { font-size: 20px; color: #1F2937; font-weight: 700; }
            QLabel { font-size: 14px; color: #374151; }
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QPushButton#primary {
                padding: 10px 16px;
                background-color: #2E7D32;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#primary:hover { background-color: #1B5E20; }
            QPushButton#secondary {
                padding: 10px 16px;
                background-color: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#secondary:hover { background-color: #F3F4F6; }
            QFrame#preview {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #FAFAFA;
            }
        """)
        self.resize(520, 360)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)

        self.title = QLabel("Adicionar Nova Família")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        form_row = QHBoxLayout()
        form_row.setSpacing(12)
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.label_nome = QLabel("Nome da Família")
        self.input_nome = QLineEdit()
        left.addWidget(self.label_nome)
        left.addWidget(self.input_nome)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("preview")
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        self.preview_label = QLabel("Prévia da foto")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_pix = QLabel()
        self.preview_pix.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.preview_pix)
        right.addWidget(self.preview_frame)

        form_row.addLayout(left, 1)
        form_row.addLayout(right, 1)
        self.layout.addLayout(form_row)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.botao_escolher_foto = QPushButton("Selecionar Foto")
        self.botao_escolher_foto.setObjectName("secondary")
        self.botao_escolher_foto.clicked.connect(self.escolher_foto)
        actions.addWidget(self.botao_escolher_foto)

        self.botao_salvar = QPushButton("Salvar")
        self.botao_salvar.setObjectName("primary")
        self.botao_salvar.clicked.connect(self.salvar_familia)
        actions.addWidget(self.botao_salvar)

        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.setObjectName("secondary")
        self.botao_cancelar.clicked.connect(self.reject)
        actions.addWidget(self.botao_cancelar)

        self.layout.addLayout(actions)

        self.caminho_foto = None
        self.data_manager = DataManager()

    def showEvent(self, event):
        super().showEvent(event)
        self.reset_fields()

    def reset_fields(self):
        self.input_nome.clear()
        self.caminho_foto = None
        self.preview_pix.clear()
        self.preview_label.setText("Prévia da foto")

    def escolher_foto(self):
        file_dialog = QFileDialog()
        caminho, _ = file_dialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if caminho:
            self.caminho_foto = caminho
            pix = QPixmap(caminho)
            if not pix.isNull():
                scaled = pix.scaled(220, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_pix.setPixmap(scaled)

    def salvar_familia(self):
        nome = self.input_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Erro", "Informe o nome da família.")
            return
        if not self.caminho_foto:
            QMessageBox.warning(self, "Erro", "Escolha uma foto válida (.png, .jpg, .jpeg).")
            return
        ok = self.data_manager.adicionar_familia(nome, self.caminho_foto)
        if not ok:
            QMessageBox.warning(self, "Erro", "Não foi possível adicionar a família. Verifique os dados.")
            return
        QMessageBox.information(self, "Sucesso", f"Família '{nome}' adicionada com sucesso!")
        self.familia_adicionada.emit()
        self.accept()
