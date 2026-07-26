from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QGuiApplication, QFont, QMovie
from PySide6.QtCore import Qt, Signal, QTimer, QSize
import os
import sys

from .data_manager import DataManager
from .widgets import TitleLabel
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
        self.setFixedSize(1024, 768)
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        self.subtitulo = TitleLabel("Última família no Altar", size=40)
        self.layout.addWidget(self.subtitulo)

        self.nome_ultima = TitleLabel("", size=32)

        self.imagem_ultima = ResponsiveImage(self)
        self.imagem_ultima.setMinimumHeight(600)
        self.layout.addWidget(self.imagem_ultima, stretch=1)
        # Nome sobreposto à última família
        self.nome_ultima.setParent(self.imagem_ultima)
        self.nome_ultima.setStyleSheet(self._overlay_style())
        self.nome_ultima.hide()
        self.numero_ultima = TitleLabel("", size=32)
        self.numero_ultima.setParent(self.imagem_ultima)
        self.numero_ultima.setStyleSheet(self._overlay_style())
        self.numero_ultima.hide()

        self.imagem_label = ResponsiveImage(self)
        # Título da família sobre a foto (overlay)
        self.titulo_atual = TitleLabel("", size=48)
        self.titulo_atual.setParent(self.imagem_label)
        self.titulo_atual.hide()
        self.titulo_atual.setStyleSheet(self._overlay_style(padding_vertical=10, padding_horizontal=20))
        self.numero_atual = TitleLabel("", size=48)
        self.numero_atual.setParent(self.imagem_label)
        self.numero_atual.hide()
        self.numero_atual.setStyleSheet(self._overlay_style(padding_vertical=10, padding_horizontal=20))
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
        
        # Sem elementos de loading

        self.move_to_second_screen()
        self.show()

        self.atualizar_ultimo_sorteado()
        if self._numero_param:
            QTimer.singleShot(50, lambda: self.mostrar_familia_por_numero(self._numero_param))
        QTimer.singleShot(100, self.ready.emit)

    def _overlay_style(self, padding_vertical=8, padding_horizontal=16):
        return (
            "color: #FFFFFF; "
            "background-color: rgba(0,0,0,140); "
            f"padding: {padding_vertical}px {padding_horizontal}px; "
            "border-radius: 12px;"
        )

    def _set_overlay_number(self, label, numero, parent_widget):
        label.setText(str(numero))
        font = label.font()
        largura = max(parent_widget.width(), 1)
        pixel_size = max(18, min(36, int(largura * 0.038)))
        font.setPixelSize(pixel_size)
        label.setFont(font)
        label.adjustSize()
        max_width = max(140, parent_widget.width() - 32)
        label.setMaximumWidth(max_width)
        label.show()

    def _position_overlay_bottom_right(self, label, parent_widget, margin=16):
        if not label.isVisible():
            return
        label.adjustSize()
        x = max(margin, parent_widget.width() - label.width() - margin)
        y = max(margin, parent_widget.height() - label.height() - margin)
        label.move(x, y)

    def atualizar_ultimo_sorteado(self):
        numero = self.data_manager.carregar_ultimo_sorteio()
        if not numero:
            self.imagem_ultima.set_pixmap(None)
            self.nome_ultima.setText("Nenhuma família sorteada ainda.")
            self.numero_ultima.hide()
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
            self.nome_ultima.show()
            self._set_overlay_number(self.numero_ultima, familia.get("numero", "-"), self.imagem_ultima)
            QTimer.singleShot(0, self._reposicionar_overlays)
        else:
            self.imagem_ultima.set_pixmap(None)
            self.nome_ultima.setText("Família não encontrada.")
            self.numero_ultima.hide()

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
        QTimer.singleShot(100, lambda: self.realizar_sorteio(familia))

    def realizar_sorteio(self, familia):
        self.imagem_ultima.hide()
        self.nome_ultima.hide()
        self.numero_ultima.hide()
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
        self._set_overlay_number(self.numero_atual, familia.get("numero", "-"), self.imagem_label)
        self._reposicionar_overlays()

        # Exibe somente foto e nome sobreposto

        self.sorteioRealizado.emit(str(familia.get("numero")))

    def exibir_mensagem(self, texto):
        self.mensagem_label.setText(texto)
        self.mensagem_label.show()
        QTimer.singleShot(3000, self.mensagem_label.hide)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposicionar_overlays()

    def _reposicionar_overlays(self):
        if hasattr(self, 'titulo_atual') and self.titulo_atual.isVisible():
            self.titulo_atual.setFixedWidth(self.imagem_label.width())
            self.titulo_atual.move(0, 12)
        if hasattr(self, 'numero_atual') and self.numero_atual.isVisible():
            self._position_overlay_bottom_right(self.numero_atual, self.imagem_label, margin=16)
        if hasattr(self, 'nome_ultima') and self.nome_ultima.isVisible():
            self.nome_ultima.setFixedWidth(self.imagem_ultima.width())
            self.nome_ultima.move(0, 12)
        if hasattr(self, 'numero_ultima') and self.numero_ultima.isVisible():
            self._position_overlay_bottom_right(self.numero_ultima, self.imagem_ultima, margin=16)

    def move_to_second_screen(self):
        screens = QGuiApplication.screens()
        if len(screens) > 1:
            second = screens[1]
            geom = second.geometry()
            self.move(geom.left(), geom.top())

    def obter_caminho_arquivo(self, caminho):
        dm = DataManager()
        return dm._resolve_photo_abs(caminho) if caminho else ""

    def _position_current_name(self):
        pass
