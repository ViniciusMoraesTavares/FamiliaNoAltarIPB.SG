from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QGuiApplication, QFont, QMovie
from PySide6.QtCore import Qt, Signal, QTimer, QSize
import json
import os


class JanelaSorteio(QWidget):
    sorteioRealizado = Signal(str)  # Sinal emitido com o número sorteado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sorteio - Família no Altar")
        self.setStyleSheet("background-color: #ffffff;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 30, 50, 30)
        self.layout.setSpacing(20)

        # Título
        titulo = QLabel("Família no Altar")
        titulo.setFont(QFont("Arial", 40, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #00796B;")
        self.layout.addWidget(titulo)

        # Subtítulo
        self.subtitulo = QLabel("Última família no Altar")
        self.subtitulo.setFont(QFont("Arial", 24))
        self.subtitulo.setAlignment(Qt.AlignCenter)
        self.subtitulo.setStyleSheet("color: #00796B;")
        self.layout.addWidget(self.subtitulo)

        # Imagem e nome da última sorteada
        self.imagem_ultima = QLabel(alignment=Qt.AlignCenter)
        self.imagem_ultima.setStyleSheet("border-radius: 20px;")
        self.layout.addWidget(self.imagem_ultima)

        self.nome_ultima = QLabel()
        self.nome_ultima.setFont(QFont("Arial", 22, QFont.Bold))
        self.nome_ultima.setAlignment(Qt.AlignCenter)
        self.nome_ultima.setStyleSheet("color: #004d40;")
        self.layout.addWidget(self.nome_ultima)

        # Mensagem de erro
        self.mensagem_label = QLabel()
        self.mensagem_label.setFont(QFont("Arial", 20))
        self.mensagem_label.setStyleSheet("color: red;")
        self.mensagem_label.setAlignment(Qt.AlignCenter)
        self.mensagem_label.hide()
        self.layout.addWidget(self.mensagem_label)

        # Imagem e nome da família sorteada
        self.imagem_label = QLabel(alignment=Qt.AlignCenter)
        self.imagem_label.setStyleSheet("border-radius: 20px;")
        self.layout.addWidget(self.imagem_label)

        self.nome_label = QLabel()
        self.nome_label.setFont(QFont("Arial", 32, QFont.Bold))
        self.nome_label.setAlignment(Qt.AlignCenter)
        self.nome_label.setStyleSheet("color: #00796B;")
        self.layout.addWidget(self.nome_label)

        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Animação de loading
        self.loading_label = QLabel(alignment=Qt.AlignCenter)
        self.loading_movie = QMovie("dados/loading.gif")
        self.loading_movie.setScaledSize(QSize(100, 100))
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        self.layout.addWidget(self.loading_label)

        # Campo de número
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Número")
        self.numero_input.setFont(QFont("Arial", 24))
        self.numero_input.setAlignment(Qt.AlignCenter)
        self.numero_input.setMaxLength(3)
        self.numero_input.setFixedWidth(200)
        self.numero_input.setStyleSheet(""" 
            QLineEdit {
                padding: 10px;
                font-size: 24px;
                border: 2px solid #00796B;
                border-radius: 8px;
                background-color: #ffffff;
            }
        """)
        self.numero_input.returnPressed.connect(self.validar_numero_para_sorteio)
        self.layout.addWidget(self.numero_input, alignment=Qt.AlignHCenter | Qt.AlignBottom)

        self.setLayout(self.layout)
        self.move_to_second_screen()
        self.showFullScreen()

        # Atualiza o último sorteio na tela
        self.atualizar_ultimo_sorteado()

    def atualizar_ultimo_sorteado(self):
        numero = carregar_ultimo_sorteio()
        if not numero:
            self.imagem_ultima.clear()
            self.nome_ultima.setText("Nenhuma família sorteada ainda.")
            return

        familias = carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if familia:
            foto_path = familia.get("foto", "")
            if os.path.exists(foto_path):
                pixmap = QPixmap(foto_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imagem_ultima.setPixmap(pixmap)
            else:
                self.imagem_ultima.setText("Foto não encontrada")
            self.nome_ultima.setText(familia.get("nome", "Família Sem Nome"))
        else:
            self.imagem_ultima.clear()
            self.nome_ultima.setText("Família não encontrada.")

    def validar_numero_para_sorteio(self):
        self.mensagem_label.hide()
        numero = self.numero_input.text().strip()

        if not numero:
            self.exibir_mensagem("Digite um número válido.")
            return

        familias = carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == numero), None)

        if not familia:
            self.exibir_mensagem(f"Família número {numero} não existe.")
            return

        if familia.get("sorteado"):
            self.exibir_mensagem(f"A família número {numero} já foi sorteada.")
            return

        self.loading_label.show()
        self.loading_movie.start()
        QTimer.singleShot(1000, self.realizar_sorteio)

    def realizar_sorteio(self):
        self.loading_label.hide()
        self.loading_movie.stop()

        numero = self.numero_input.text().strip()
        familias = carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == numero), None)

        if not familia:
            return

        foto_path = familia.get("foto", "")
        if os.path.exists(foto_path):
            pixmap = QPixmap(foto_path).scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagem_label.setPixmap(pixmap)
        else:
            self.imagem_label.setText("Foto não encontrada")
            self.imagem_label.setStyleSheet("font-size: 20px; color: red;")

        self.nome_label.setText(familia.get("nome", "Família Sem Nome"))

        # Atualiza o título para mostrar que a família foi sorteada
        self.subtitulo.setText("Família no Altar da Semana")
        self.imagem_ultima.clear()
        self.nome_ultima.clear()

        # Envia o número sorteado ao painel
        self.sorteioRealizado.emit(numero)

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

# Funções auxiliares (fora da classe)
def carregar_familias():
    try:
        with open("dados/familias.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def carregar_ultimo_sorteio():
    try:
        with open("dados/sorteio.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("ultimo_sorteado", None)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo sorteio.json")
        return None
