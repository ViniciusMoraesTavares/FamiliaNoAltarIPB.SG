from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QGuiApplication, QFont, QMovie
from PySide6.QtCore import Qt, Signal, QTimer, QSize
import os

from .data_manager import DataManager
from .widgets import TitleLabel, ImageContainer, LoadingOverlay
from .styles import AppStyles

class JanelaSorteio(QWidget):
    sorteioRealizado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sorteio - Família no Altar")
        self.setStyleSheet("background-color: #ffffff;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.data_manager = DataManager()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 30, 50, 30)
        self.layout.setSpacing(20)

        # Título
        titulo = TitleLabel("Família no Altar", size=40)
        self.layout.addWidget(titulo)

        # Subtítulo
        self.subtitulo = TitleLabel("Última família no Altar", size=24)
        self.layout.addWidget(self.subtitulo)

        # Imagem e nome da última sorteada
        self.imagem_ultima = ImageContainer(self)
        self.imagem_ultima.image_label.setFixedSize(600, 600)
        self.layout.addWidget(self.imagem_ultima)

        self.nome_ultima = TitleLabel("", size=22, color="#004d40")
        self.layout.addWidget(self.nome_ultima)

        # Mensagem de erro
        self.mensagem_label = QLabel()
        self.mensagem_label.setFont(QFont("Segoe UI", 20))
        self.mensagem_label.setStyleSheet("color: red;")
        self.mensagem_label.setAlignment(Qt.AlignCenter)
        self.mensagem_label.hide()
        self.layout.addWidget(self.mensagem_label)

        # Imagem e nome da família sorteada
        self.imagem_label = ImageContainer(self)
        self.imagem_label.image_label.setFixedSize(600, 600)
        self.layout.addWidget(self.imagem_label)

        self.nome_label = TitleLabel("", size=32)
        self.layout.addWidget(self.nome_label)

        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Campo de número
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Número")
        self.numero_input.setFont(QFont("Segoe UI", 24))
        self.numero_input.setAlignment(Qt.AlignCenter)
        self.numero_input.setMaxLength(3)
        self.numero_input.setFixedWidth(200)
        self.numero_input.setStyleSheet(AppStyles.input_style())
        self.numero_input.returnPressed.connect(self.validar_numero_para_sorteio)
        self.layout.addWidget(self.numero_input, alignment=Qt.AlignHCenter | Qt.AlignBottom)

        self.setLayout(self.layout)
        
        # Loading overlay
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.resize(self.size())

        self.move_to_second_screen()
        self.showFullScreen()

        # Atualiza o último sorteio na tela
        self.atualizar_ultimo_sorteado()

    def atualizar_ultimo_sorteado(self):
        numero = self.data_manager.carregar_ultimo_sorteio()
        if not numero:
            self.imagem_ultima.set_image(None)
            self.nome_ultima.setText("Nenhuma família sorteada ainda.")
            return

        familias = self.data_manager.carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if familia:
            foto_path = familia.get("foto", "")
            if os.path.exists(foto_path):
                pixmap = QPixmap(foto_path).scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imagem_ultima.set_image(pixmap)
            self.nome_ultima.setText(familia.get("nome", "Família Sem Nome"))
        else:
            self.imagem_ultima.set_image(None)
            self.nome_ultima.setText("Família não encontrada.")

    def validar_numero_para_sorteio(self):
        self.mensagem_label.hide()
        numero = self.numero_input.text().strip()

        if not numero:
            self.exibir_mensagem("Digite um número válido.")
            return

        familias = self.data_manager.carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == numero), None)

        if not familia:
            self.exibir_mensagem(f"Família número {numero} não existe.")
            return

        if familia.get("sorteado"):
            self.exibir_mensagem(f"A família número {numero} já foi sorteada.")
            return

        self.loading_overlay.show()
        QTimer.singleShot(1000, lambda: self.realizar_sorteio(familia))

    def realizar_sorteio(self, familia):
        self.loading_overlay.hide()

        # Limpa a seção da última família sorteada
        self.imagem_ultima.hide()
        self.nome_ultima.hide()

        # Mostra a nova família sorteada
        foto_path = familia.get("foto", "")
        if os.path.exists(foto_path):
            pixmap = QPixmap(foto_path).scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagem_label.set_image(pixmap)

        self.nome_label.setText(familia.get("nome", "Família Sem Nome"))

        # Atualiza o título para mostrar que a família foi sorteada
        self.subtitulo.setText("Família no Altar da Semana")

        # Envia o número sorteado ao painel
        self.sorteioRealizado.emit(str(familia.get("numero")))

    def exibir_mensagem(self, texto):
        self.mensagem_label.setText(texto)
        self.mensagem_label.show()
        QTimer.singleShot(3000, self.mensagem_label.hide)

    def move_to_second_screen(self):
        screens = QGuiApplication.screens()
        if len(screens) > 1:
            second = screens[1]
            geom = second.geometry()
            self.move(geom.left(), geom.top())
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.loading_overlay:
            self.loading_overlay.resize(self.size())
