from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
import os
import shutil
from uuid import uuid4
from src.utils import carregar_familias, salvar_familias
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

FOTOS_PATH = os.path.join(BASE_PATH, "imagens", "familias")

class JanelaEditarFamilia(QWidget):
    def __init__(self, familia, callback_atualizacao):
        super().__init__()
        self.familia = familia
        self.callback_atualizacao = callback_atualizacao
        self.old_photo_path = familia.get("foto", "")  
        self.caminho_foto = None

        os.makedirs(FOTOS_PATH, exist_ok=True)

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
        file_dialog = QFileDialog()
        caminho, _ = file_dialog.getOpenFileName(
            self, "Selecionar nova foto", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if caminho:
            self.caminho_foto = caminho
            QMessageBox.information(self, "Foto Selecionada", "Foto selecionada com sucesso!")
            pixmap = QPixmap(caminho).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(pixmap)

    def _should_delete_old_photo(self):
        if not self.old_photo_path or not os.path.exists(self.old_photo_path):
            return False

        familias = carregar_familias()
        for f in familias:
            if f.get("numero") != self.familia.get("numero") and f.get("foto") == self.old_photo_path:
                return False

        return True

    def salvar_edicao(self):
        novo_nome = self.nome_input.text().strip()
        if novo_nome:
            self.familia["nome"] = novo_nome

        if self.caminho_foto:
            extensao = os.path.splitext(self.caminho_foto)[-1]
            novo_nome_arquivo = f"{uuid4().hex[:8]}{extensao}"
            caminho_destino = os.path.join(FOTOS_PATH, novo_nome_arquivo)
            shutil.copy2(self.caminho_foto, caminho_destino)

            novo_caminho_foto = os.path.join("imagens", "familias", novo_nome_arquivo).replace("\\", "/")
            self.familia["foto"] = os.path.join(BASE_PATH, novo_caminho_foto).replace("\\", "/")

            if self._should_delete_old_photo():
                try:
                    os.remove(self.old_photo_path)
                except Exception as e:
                    print(f"Erro ao deletar foto antiga: {str(e)}")

        familias = carregar_familias()
        for i, f in enumerate(familias):
            if f.get("numero") == self.familia.get("numero"):
                familias[i] = self.familia
                break

        salvar_familias(familias)

        if self.callback_atualizacao:
            self.callback_atualizacao()

        self.close()
