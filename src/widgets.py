from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QWidget, QLineEdit, QToolButton, QDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont, QPixmap, QMovie, QColor
import os
from .styles import AppStyles
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

class NotificationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QFrame {
                background-color: #4CAF50;
                border-radius: 8px;
                color: white;
            }
        """)
        
        shadow = AppStyles.get_shadow_effect()
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.message_label)
        
        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setStyleSheet("""
            QToolButton {
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #E8F5E9;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        self.hide()
        
    def show_message(self, message, type="success", auto_hide=True):
        colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "info": "#2196F3"
        }
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.get(type, colors["info"])};
                border-radius: 8px;
                color: white;
            }}
        """)
        self.message_label.setText(message)
        self.show()
        if auto_hide:
            QTimer.singleShot(3000, self.hide)

class AutoSaveBanner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border-bottom: 1px solid #C8E6C9;
            }
            QLabel {
                color: #2E7D32;
                font-size: 12px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.status_label = QLabel("✓ Todas as alterações salvas")
        layout.addWidget(self.status_label)
        
        self._opacity = 1.0
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #E8F5E9;
                border-bottom: 1px solid #C8E6C9;
                opacity: {value};
            }}
            QLabel {{
                color: #2E7D32;
                font-size: 12px;
            }}
        """)
        
    opacity = Property(float, get_opacity, set_opacity)
    
    def show_saving(self):
        self.status_label.setText("💾 Salvando alterações...")
        self._animation.setStartValue(0.7)
        self._animation.setEndValue(1.0)
        self._animation.start()
        
    def show_saved(self):
        self.status_label.setText("✓ Todas as alterações salvas")
        QTimer.singleShot(2000, self.fade_out)
        
    def fade_out(self):
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.7)
        self._animation.start()

class BaseCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(AppStyles.card_style())
        self.setGraphicsEffect(AppStyles.get_shadow_effect())
        self._init_layout()
    
    def _init_layout(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

class StatusBadge(QFrame):
    def __init__(self, text, is_active=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border-radius: 12px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        icon = "✓" if is_active else "⏳"
        label = QLabel(f"{icon} {text}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "color: #2E7D32; font-weight: bold;" if is_active 
            else "color: #757575; font-style: italic;"
        )
        layout.addWidget(label)

class TitleLabel(QLabel):
    def __init__(self, text, size=28, color=AppStyles.PRIMARY_COLOR, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", size, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"color: {color};")

class ImageContainer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                min-height: 120px;
            }
            QLabel {
                border-radius: 8px;
            }
            QLabel:hover {
                background-color: #E8F5E9;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 120)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
    
    def set_image(self, pixmap=None):
        if pixmap:
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                }
            """)
        else:
            self.image_label.setText("📷")
            self.image_label.setFont(QFont("Segoe UI", 40))
            self.image_label.setStyleSheet("""
                QLabel {
                    color: #9E9E9E;
                }
            """)
    
    def clear(self):
        self.image_label.clear()
        self.image_label.setText("📷")
        self.image_label.setFont(QFont("Segoe UI", 40))
        self.image_label.setStyleSheet("""
            QLabel {
                color: #9E9E9E;
            }
        """)

class FamilyCard(BaseCard):
    edit_clicked = Signal(dict)
    delete_clicked = Signal(dict)
    image_clicked = Signal(str)
    
    def __init__(self, familia, parent=None):
        super().__init__(parent)
        self.familia = familia
        self._setup_ui()
    
    def _setup_ui(self):
        img_container = ImageContainer(self)
        caminho = self.familia.get("foto", "")
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_container.set_image(pixmap)
        else:
            img_container.clear()
            
        img_container.image_label.mousePressEvent = lambda event: self._on_image_clicked(caminho)
        self.layout.addWidget(img_container)
        
        nome_label = QLabel(self.familia.get("nome", "Sem Nome"))
        nome_label.setAlignment(Qt.AlignCenter)
        nome_label.setStyleSheet("""QLabel { font-size: 16px; font-weight: bold; color: #212121; }""")
        self.layout.addWidget(nome_label)
        
        numero_label = QLabel(f"Número: {self.familia.get('numero', '-')}")
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("""QLabel { color: #757575; font-size: 14px; }""")
        self.layout.addWidget(numero_label)
        
        status = "Sorteado" if self.familia.get("sorteado") else "Aguardando"
        status_badge = StatusBadge(status, self.familia.get("sorteado"))
        self.layout.addWidget(status_badge)
        
        if self.familia.get("sorteado") and self.familia.get("data_sorteio"):
            data_label = QLabel(f"📅 {self.familia.get('data_sorteio')}")
            data_label.setAlignment(Qt.AlignCenter)
            data_label.setStyleSheet("""QLabel { color: #757575; font-size: 12px; }""")
            self.layout.addWidget(data_label)
        
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(4)
        botoes_layout.setContentsMargins(0, 0, 0, 0)
        
        editar_btn = QPushButton("✎")
        editar_btn.clicked.connect(lambda: self.edit_clicked.emit(self.familia))
        editar_btn.setStyleSheet("""QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px; border-radius: 6px; font-size: 18px; font-weight: bold; min-width: 32px; max-width: 32px; font-family: 'Segoe UI Symbol', 'Segoe UI'; } QPushButton:hover { background-color: #43A047; }""")
        editar_btn.setFixedSize(32, 32)
        
        excluir_btn = QPushButton("🗑️")
        excluir_btn.clicked.connect(lambda: self.delete_clicked.emit(self.familia))
        excluir_btn.setStyleSheet("""QPushButton { background-color: #EF5350; color: white; border: none; padding: 8px; border-radius: 6px; font-size: 16px; font-weight: bold; min-width: 32px; max-width: 32px; } QPushButton:hover { background-color: #E53935; }""")
        excluir_btn.setFixedSize(32, 32)
        
        botoes_layout.addWidget(editar_btn)
        botoes_layout.addWidget(excluir_btn)
        botoes_layout.addStretch()
        botoes_container = QWidget()
        botoes_container.setLayout(botoes_layout)
        self.layout.addWidget(botoes_container, alignment=Qt.AlignCenter)

    def _on_image_clicked(self, caminho_imagem):
        if os.path.exists(caminho_imagem):
            viewer = FullscreenImageViewer(caminho_imagem, self)
            viewer.exec_()

class FullscreenImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.7);
            }
            QLabel {
                background-color: white;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #EF5350;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)

        self.original_pixmap = QPixmap(image_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close_with_animation)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.photo_container = QFrame()
        self.photo_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        photo_layout = QVBoxLayout(self.photo_container)
        photo_layout.setContentsMargins(10, 10, 10, 10)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        photo_layout.addWidget(self.photo_label)

        layout.addWidget(self.photo_container, alignment=Qt.AlignCenter)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width(), screen.height())
        self.move(0, 0)

        self._update_image_size()
        self.fade_animation.start()

    def _update_image_size(self):
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)

        orig_width = self.original_pixmap.width()
        orig_height = self.original_pixmap.height()

        width_ratio = max_width / orig_width
        height_ratio = max_height / orig_height
        scale_factor = min(width_ratio, height_ratio)

        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)

        scaled_pixmap = self.original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.photo_label.setPixmap(scaled_pixmap)
        self.photo_container.setFixedSize(new_width + 20, new_height + 20)

    def close_with_animation(self):
        self.fade_animation.setDirection(QPropertyAnimation.Backward)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()

    def mousePressEvent(self, event):
        container_pos = self.photo_container.mapFrom(self, event.pos())
        if not self.photo_container.rect().contains(container_pos):
            self.close_with_animation()
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_with_animation()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image_size()

class SearchBar(QFrame):
    textChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #E0E0E0;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; background: transparent;")
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Pesquisar por nome ou número...")
        self.input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                padding: 8px;
            }
        """)
        self.input.textChanged.connect(self.textChanged.emit)
        
        layout.addWidget(search_icon)
        layout.addWidget(self.input)
    
    def text(self):
        return self.input.text()
    
    def clear(self):
        self.input.clear()

class FilterButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #757575;
                border: none;
                padding: 8px 15px;
                border-radius: 15px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: #E8F5E9;
            }
        """)

class LoadingOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 180);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.loading_label = QLabel()
        self.loading_movie = QMovie(os.path.join(BASE_PATH, "imagens", "loading.gif"))
        self.loading_movie.setScaledSize(QSize(300, 300))
        self.loading_label.setMovie(self.loading_movie)
        layout.addWidget(self.loading_label)
        
        self.setVisible(False)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.loading_movie.start()
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.loading_movie.stop()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())

class PhotoViewer(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.7);
            }
            QLabel {
                background-color: white;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #EF5350;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)

        self.original_pixmap = pixmap

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close_with_animation)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.photo_container = QFrame()
        self.photo_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        photo_layout = QVBoxLayout(self.photo_container)
        photo_layout.setContentsMargins(10, 10, 10, 10)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        photo_layout.addWidget(self.photo_label)

        layout.addWidget(self.photo_container, alignment=Qt.AlignCenter)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width(), screen.height())
        self.move(0, 0)

        self._update_image_size()

        self.fade_animation.start()

    def _update_image_size(self):
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)

        orig_width = self.original_pixmap.width()
        orig_height = self.original_pixmap.height()

        width_ratio = max_width / orig_width
        height_ratio = max_height / orig_height
        scale_factor = min(width_ratio, height_ratio)

        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)

        scaled_pixmap = self.original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.photo_label.setPixmap(scaled_pixmap)

        self.photo_container.setFixedSize(new_width + 20, new_height + 20)

    def close_with_animation(self):
        self.fade_animation.setDirection(QPropertyAnimation.Backward)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()

    def mousePressEvent(self, event):
        container_pos = self.photo_container.mapFrom(self, event.pos())
        
        if not self.photo_container.rect().contains(container_pos):
            self.close_with_animation()
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_with_animation()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image_size() 