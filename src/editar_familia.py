from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
import os
from src.utils import carregar_familias, salvar_familias

class JanelaEditarFamilia(QWidget):
    def __init__(self, familia, callback_atualizar):
        super().__init__()
        self.familia = familia
        self.callback_atualizar = callback_atualizar

        self.setWindowTitle("✏️ Editar Família")
        self.setMinimumSize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.foto_label = QLabel()
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.carregar_foto()
        layout.addWidget(self.foto_label)

        btn_trocar_foto = QPushButton("📷 Trocar Foto")
        btn_trocar_foto.clicked.connect(self.selecionar_foto)
        layout.addWidget(btn_trocar_foto, alignment=Qt.AlignCenter)

        self.nome_input = QLineEdit(self.familia.get("nome", ""))
        self.nome_input.setPlaceholderText("Nome da família")
        self.nome_input.setStyleSheet("font-size: 16px; padding: 8px;")
        layout.addWidget(self.nome_input)

        botoes = QHBoxLayout()

        salvar_btn = QPushButton("💾 Salvar")
        salvar_btn.clicked.connect(self.salvar_edicao)
        botoes.addWidget(salvar_btn)

        cancelar_btn = QPushButton("❌ Cancelar")
        cancelar_btn.clicked.connect(self.close)
        botoes.addWidget(cancelar_btn)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def carregar_foto(self):
        caminho = self.familia.get("foto", "")
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(pixmap)
        else:
            self.foto_label.setText("📷")
            self.foto_label.setFont(QFont("Arial", 50))

    def selecionar_foto(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar nova foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if caminho:
            self.familia["foto"] = caminho
            self.carregar_foto()

    def salvar_edicao(self):
        novo_nome = self.nome_input.text().strip()
        if novo_nome:
            self.familia["nome"] = novo_nome

        familias = carregar_familias()
        for i, f in enumerate(familias):
            if f.get("numero") == self.familia.get("numero"):
                familias[i] = self.familia
                break

        salvar_familias(familias)
        
        # Chama o callback antes de fechar a janela
        if self.callback_atualizar:
            self.callback_atualizar()
            
        self.close()
