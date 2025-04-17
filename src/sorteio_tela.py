from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QGuiApplication, QFont
from PySide6.QtCore import Qt, Signal
import json
import os


def carregar_familias():
    try:
        with open("dados/familias.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def salvar_sorteio(numero):
    try:
        with open("dados/sorteio.json", "w", encoding="utf-8") as f:
            json.dump({"numero_sorteado": numero}, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Erro ao salvar sorteio:", e)


class JanelaSorteio(QWidget):
    sorteioRealizado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sorteio - Família no Altar")
        self.setStyleSheet("background-color: #fdfdfd;")
        self.setWindowFlags(Qt.FramelessWindowHint)  # sem botões de fechar
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(30)

        # Campo de entrada do número
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Digite o número da família e pressione Enter")
        self.numero_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                font-size: 24px;
                border: 2px solid #00796B;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)
        self.numero_input.returnPressed.connect(self.realizar_sorteio)
        self.layout.addWidget(self.numero_input, alignment=Qt.AlignCenter)

        # Espaço para a imagem
        self.imagem_label = QLabel()
        self.imagem_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imagem_label, alignment=Qt.AlignCenter)

        # Espaço para o nome da família
        self.nome_label = QLabel()
        self.nome_label.setAlignment(Qt.AlignCenter)
        self.nome_label.setFont(QFont("Arial", 30, QFont.Bold))
        self.nome_label.setStyleSheet("color: #00796B;")
        self.layout.addWidget(self.nome_label, alignment=Qt.AlignCenter)

        # Espaço entre os elementos
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(self.layout)
        self.move_to_second_screen()
        self.showFullScreen()

    def move_to_second_screen(self):
        screens = QGuiApplication.screens()
        if len(screens) > 1:
            second = screens[1]
            geom = second.geometry()
            self.move(geom.left(), geom.top())

    def realizar_sorteio(self):
        numero = self.numero_input.text().strip()
        if not numero:
            QMessageBox.warning(self, "Aviso", "Digite um número válido.")
            return

        familias = carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == numero), None)

        if not familia:
            QMessageBox.warning(self, "Erro", "Família não encontrada.")
            return

        if familia.get("sorteado"):
            QMessageBox.warning(self, "Erro", "Essa família já foi sorteada.")
            return

        # Mostra a imagem da família
        foto_path = familia.get("foto", "")
        if os.path.exists(foto_path):
            pixmap = QPixmap(foto_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagem_label.setPixmap(pixmap)
        else:
            self.imagem_label.setText("Foto não encontrada")
            self.imagem_label.setStyleSheet("font-size: 20px; color: red;")

        # Mostra o nome da família
        self.nome_label.setText(familia.get("nome", "Família Sem Nome"))

        # Emite sinal e salva o número sorteado
        self.sorteioRealizado.emit(numero)
        salvar_sorteio(numero)
