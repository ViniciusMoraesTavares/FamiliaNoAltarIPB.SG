from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QMessageBox, QFrame
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

        self.setWindowTitle("Editar Família")
        self.setMinimumSize(560, 420)
        self.setWindowModality(Qt.ApplicationModal)

        self.init_ui()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # Área de prévia da foto
        photo_card = QFrame()
        photo_card.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }")
        photo_layout = QVBoxLayout(photo_card)
        photo_layout.setContentsMargins(12, 12, 12, 12)
        photo_layout.setSpacing(10)

        self.foto_label = QLabel()
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setMinimumSize(260, 260)
        self.carregar_foto()
        photo_layout.addWidget(self.foto_label)

        btn_trocar_foto = QPushButton("Trocar foto")
        btn_trocar_foto.setStyleSheet("QPushButton { background-color: #FFFFFF; color: #374151; border: 1px solid #D1D5DB; border-radius: 8px; padding: 8px 12px; } QPushButton:hover { background-color: #F3F4F6; }")
        btn_trocar_foto.clicked.connect(self.selecionar_foto)
        photo_layout.addWidget(btn_trocar_foto, alignment=Qt.AlignCenter)

        # Área de edição (direita)
        form = QVBoxLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        nome_label = QLabel("Nome da família")
        nome_label.setStyleSheet("color: #374151; font-size: 13px; margin-bottom: 4px;")
        self.nome_input = QLineEdit(self.familia.get("nome", ""))
        self.nome_input.setPlaceholderText("Ex.: Família Silva")
        self.nome_input.setStyleSheet("QLineEdit { padding: 10px; font-size: 16px; border: 1px solid #D1D5DB; border-radius: 8px; background: #FFFFFF; } QLineEdit:focus { border-color: #2c4b23; }")
        form.addWidget(nome_label)
        form.addWidget(self.nome_input)

        # Controle de status (toggle switch)
        status_label = QLabel("Status")
        status_label.setStyleSheet("color: #374151; font-size: 13px; margin-bottom: 4px;")
        form.addWidget(status_label)
        self.status_button = QPushButton()
        self.status_button.setCursor(Qt.PointingHandCursor)
        self.status_button.setFixedHeight(36)
        self.status_button.setStyleSheet("QPushButton { border-radius: 18px; padding: 6px 14px; font-weight: 700; }")
        self._status_value = bool(self.familia.get("sorteado", False))
        self._update_status_button_style()
        self.status_button.clicked.connect(self._on_status_button_clicked)
        form.addWidget(self.status_button)
        status_hint = QLabel("Clique para alterar o status da família")
        status_hint.setWordWrap(True)
        status_hint.setStyleSheet("color: #6B7280; font-size: 12px; font-style: italic; margin-top: 4px;")
        form.addWidget(status_hint)

        # Ações
        actions = QHBoxLayout()
        actions.addStretch(1)
        salvar_btn = QPushButton("Salvar")
        salvar_btn.setStyleSheet("QPushButton { background-color: #2c4b23; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 700; } QPushButton:hover { background-color: #243f1d; }")
        salvar_btn.clicked.connect(self.salvar_edicao)
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("QPushButton { background-color: #FFFFFF; color: #374151; border: 1px solid #D1D5DB; border-radius: 8px; padding: 10px 16px; } QPushButton:hover { background-color: #F3F4F6; }")
        cancelar_btn.clicked.connect(self.close)
        actions.addWidget(cancelar_btn)
        actions.addWidget(salvar_btn)
        form.addLayout(actions)

        root.addWidget(photo_card, 0)
        root.addLayout(form, 1)

    def carregar_foto(self):
        caminho = self.familia.get("foto", "")
        abs_path = self.data_manager._resolve_photo_abs(caminho) if caminho else ""
        if abs_path and os.path.exists(abs_path):
            pixmap = QPixmap(abs_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
            pixmap = QPixmap(caminho).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(pixmap)

    def _foto_absoluta(self, rel_ou_abs):
        if os.path.isabs(rel_ou_abs):
            return rel_ou_abs
        return self.data_manager._resolve_photo_abs(rel_ou_abs)

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

    def _update_status_button_style(self):
        if self._status_value:
            self.status_button.setText("✓ Sorteada")
            self.status_button.setStyleSheet(
                "QPushButton { background-color: #2c4b23; color: #FFFFFF; border: none; border-radius: 18px; padding: 6px 14px; font-weight: 700; }"
                "QPushButton:hover { background-color: #243f1d; }"
            )
        else:
            self.status_button.setText("⌛ Aguardando sorteio")
            self.status_button.setStyleSheet(
                "QPushButton { background-color: #E5E7EB; color: #374151; border: 1px solid #D1D5DB; border-radius: 18px; padding: 6px 14px; font-weight: 700; }"
                "QPushButton:hover { background-color: #D1D5DB; }"
            )

    def _on_status_button_clicked(self):
        novo = not self._status_value
        from src.status_change_dialog import StatusChangeDialog
        texto = "Confirmar alteração de status da família?"
        impactos = [
            "Sorteada: define a data de sorteio para hoje.",
            "Aguardando: remove a data de sorteio.",
            "A interface será atualizada imediatamente."
        ]
        dlg = StatusChangeDialog(texto, impactos, parent=self)
        def on_confirm():
            ok = self.data_manager.alterar_status_familia(self.familia.get("numero"), novo)
            if ok:
                self._status_value = novo
                self._update_status_button_style()
                self.familia["sorteado"] = novo
                if self.callback_atualizacao:
                    self.callback_atualizacao()
            # se falhar, mantém estado visual anterior
        def on_cancel():
            pass
        dlg.confirmado.connect(on_confirm)
        dlg.cancelado.connect(on_cancel)
        dlg.show()

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
