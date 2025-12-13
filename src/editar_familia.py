from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
import os
from src.data_manager import DataManager
from src.status_change_dialog import StatusChangeDialog
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
        self.data_manager = DataManager()

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

        alterar_status_btn = QPushButton("Alterar Status")
        alterar_status_btn.clicked.connect(self.alterar_status)
        botoes.addWidget(alterar_status_btn)

        cancelar_btn = QPushButton("❌ Cancelar")
        cancelar_btn.clicked.connect(self.close)
        botoes.addWidget(cancelar_btn)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def carregar_foto(self):
        caminho = self.familia.get("foto", "")
        if not os.path.isabs(caminho):
            caminho = os.path.join(BASE_PATH, caminho)
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

    def _foto_absoluta(self, rel_ou_abs):
        return rel_ou_abs if os.path.isabs(rel_ou_abs) else os.path.join(BASE_PATH, rel_ou_abs)

    def salvar_edicao(self):
        novo_nome = self.nome_input.text().strip()
        if not novo_nome:
            QMessageBox.warning(self, "Erro", "Informe um nome válido.")
            return
        ok = self.data_manager.editar_familia(self.familia.get("numero"), novo_nome, self.caminho_foto)
        if not ok:
            QMessageBox.warning(self, "Erro", "Não foi possível salvar a edição. Verifique os dados.")
            return
        if self.callback_atualizacao:
            self.callback_atualizacao()
        self.close()

    def alterar_status(self):
        atual = bool(self.familia.get("sorteado", False))
        novo = not atual
        texto = "Esta ação irá alterar o status da família."
        impactos = [
            "Marcar como sorteada define a data de sorteio para hoje.",
            "Marcar como não sorteada remove a data de sorteio.",
            "Filtros e indicadores no painel serão atualizados.",
        ]
        dlg = StatusChangeDialog(texto, impactos, parent=self)
        dlg.confirmado.connect(lambda: self._confirmar_alteracao_status(novo))
        dlg.show()

    def _confirmar_alteracao_status(self, novo_status):
        try:
            ok = self.data_manager.alterar_status_familia(self.familia.get("numero"), novo_status)
            if not ok:
                QMessageBox.warning(self, "Erro", "Não foi possível alterar o status.")
                return
            self.familia["sorteado"] = bool(novo_status)
            if self.callback_atualizacao:
                self.callback_atualizacao()
            QMessageBox.information(self, "Sucesso", "Status alterado com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao alterar status: {str(e)}")
