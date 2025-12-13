from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QGuiApplication, QFont, QMovie
from PySide6.QtCore import Qt, Signal, QTimer, QSize
import os
import sys

from .data_manager import DataManager
from .widgets import TitleLabel, LoadingOverlay
from .styles import AppStyles

class ResponsiveImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._original = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(400)
        self._scale_ratio = 1.0
        self._scale_ratio = 1.0

    def set_pixmap(self, pixmap):
        self._original = pixmap
        self._update_scaled()
    def set_scale_ratio(self, ratio: float):
        self._scale_ratio = max(0.1, min(1.0, ratio))
        self._update_scaled()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled()

    def _update_scaled(self):
        if not self._original:
            self.clear()
            return
        w = max(1, int(self.width() * self._scale_ratio))
        h = max(1, int(self.height() * self._scale_ratio))
        scaled = self._original.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)

    def set_scale_ratio(self, ratio: float):
        try:
            r = float(ratio)
        except Exception:
            r = 1.0
        self._scale_ratio = min(1.0, max(0.6, r))
        self._update_scaled()

class JanelaSorteio(QWidget):
    sorteioRealizado = Signal(str)
    ready = Signal()

    def __init__(self, numero=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sorteio - Família no Altar")
        self.setStyleSheet("background-color: #ffffff;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.data_manager = DataManager()
        self._numero_param = numero
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 30, 50, 30)
        self.layout.setSpacing(20)

        self.subtitulo = TitleLabel("Última família no Altar", size=40)
        self.layout.addWidget(self.subtitulo)

        self.nome_ultima = TitleLabel("", size=32, color="#004d40")
        self.layout.addWidget(self.nome_ultima)

        self.imagem_ultima = ResponsiveImage(self)
        self.imagem_ultima.setMinimumHeight(600)
        self.layout.addWidget(self.imagem_ultima, stretch=1)

        self.imagem_label = ResponsiveImage(self)
        # Título da família sobre a foto (overlay)
        self.titulo_atual = TitleLabel("", size=48)
        self.titulo_atual.setParent(self.imagem_label)
        self.titulo_atual.hide()
        self.layout.addWidget(self.imagem_label)
        self.imagem_label.hide()
        self.imagem_label.set_scale_ratio(0.95)

        self.nome_label = TitleLabel("", size=32)
        self.layout.addWidget(self.nome_label)
        self.nome_label.hide()

        # Mensagens abaixo da foto atual
        self.mensagem_label = QLabel()
        self.mensagem_label.setFont(QFont("Segoe UI", 20))
        self.mensagem_label.setStyleSheet("color: red;")
        self.mensagem_label.setAlignment(Qt.AlignCenter)
        self.mensagem_label.hide()
        self.layout.addWidget(self.mensagem_label)
        # Removido spacer inferior para permitir que a imagem ocupe todo o espaço disponível

        self.setLayout(self.layout)
        # Prioriza espaço vertical para a imagem da última família
        self.layout.setStretch(0, 0)  # título
        self.layout.setStretch(1, 0)  # nome
        self.layout.setStretch(2, 1)  # imagem última família
        self.layout.setStretch(3, 0)  # mensagem
        self.layout.setStretch(4, 0)  # imagem atual (oculta inicialmente)
        self.layout.setStretch(5, 0)  # nome atual (oculto inicialmente)
        
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.resize(self.size())

        self.move_to_second_screen()
        self.showFullScreen()

        self.atualizar_ultimo_sorteado()
        if self._numero_param:
            QTimer.singleShot(50, lambda: self.mostrar_familia_por_numero(self._numero_param))
        QTimer.singleShot(100, self.ready.emit)

    def atualizar_ultimo_sorteado(self):
        numero = self.data_manager.carregar_ultimo_sorteio()
        if not numero:
            self.imagem_ultima.set_pixmap(None)
            self.nome_ultima.setText("Nenhuma família sorteada ainda.")
            return

        familias = self.data_manager.carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if familia:
            foto_path = familia.get("foto", "")
            foto_path = self.obter_caminho_arquivo(foto_path)
            if os.path.exists(foto_path):
                pixmap = QPixmap(foto_path)
                self.imagem_ultima.set_pixmap(pixmap)
                QTimer.singleShot(0, self.imagem_ultima._update_scaled)
            self.nome_ultima.setText(familia.get("nome", "Família Sem Nome"))
        else:
            self.imagem_ultima.set_pixmap(None)
            self.nome_ultima.setText("Família não encontrada.")

    def mostrar_familia_por_numero(self, numero):
        self.mensagem_label.hide()
        familias = self.data_manager.carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if not familia:
            self.exibir_mensagem(f"Família número {numero} não existe.")
            return
        if familia.get("sorteado"):
            self.exibir_mensagem(f"A família número {numero} já foi sorteada.")
            return
        self.loading_overlay.show()
        QTimer.singleShot(300, lambda: self.realizar_sorteio(familia))

    def realizar_sorteio(self, familia):
        self.loading_overlay.hide()

        self.imagem_ultima.hide()
        self.nome_ultima.hide()
        self.mensagem_label.hide()
        self.subtitulo.hide()
        self.nome_label.hide()
        self.imagem_ultima.clear()
        self.imagem_ultima.setVisible(False)

        foto_path = familia.get("foto", "")
        foto_path = self.obter_caminho_arquivo(foto_path)
        if os.path.exists(foto_path):
            pixmap = QPixmap(foto_path)
            self.imagem_label.set_pixmap(pixmap)
            self.imagem_label.show()
            self.layout.setStretch(4, 1)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)

        self.titulo_atual.setText(familia.get("nome", "Família Sem Nome"))
        self.titulo_atual.show()
        self.titulo_atual.setFixedWidth(self.imagem_label.width())
        self.titulo_atual.move(0, 10)

        # Removido título para destacar somente foto e nome

        self.sorteioRealizado.emit(str(familia.get("numero")))

    def exibir_mensagem(self, texto):
        self.mensagem_label.setText(texto)
        self.mensagem_label.show()
        QTimer.singleShot(3000, self.mensagem_label.hide)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.loading_overlay.resize(self.size())
        if hasattr(self, 'titulo_atual') and self.titulo_atual.isVisible():
            self.titulo_atual.setFixedWidth(self.imagem_label.width())
            self.titulo_atual.move(0, 10)

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

    def obter_caminho_arquivo(self, caminho):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.') 
        return os.path.join(base_path, caminho)

    def _position_current_name(self):
        pass
