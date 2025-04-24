from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QWidget, QLineEdit, QToolButton
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont, QPixmap, QMovie, QColor
import os
from .styles import AppStyles

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
        
        # Add shadow effect
        shadow = AppStyles.get_shadow_effect()
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        # Layout
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
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 120)
        self.image_label.setAlignment(Qt.AlignCenter)
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
    
    def __init__(self, familia, parent=None):
        super().__init__(parent)
        self.familia = familia
        self._setup_ui()
    
    def _setup_ui(self):
        # Image container
        img_container = ImageContainer(self)
        caminho = self.familia.get("foto", "")
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_container.set_image(pixmap)
        self.layout.addWidget(img_container)
        
        # Family name
        nome_label = QLabel(self.familia.get("nome", "Sem Nome"))
        nome_label.setAlignment(Qt.AlignCenter)
        nome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #212121;
            }
        """)
        self.layout.addWidget(nome_label)
        
        # Family number
        numero_label = QLabel(f"Número: {self.familia.get('numero', '-')}")
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(numero_label)
        
        # Status badge
        status = "Sorteado" if self.familia.get("sorteado") else "Aguardando"
        status_badge = StatusBadge(status, self.familia.get("sorteado"))
        self.layout.addWidget(status_badge)
        
        # Draw date if available
        if self.familia.get("sorteado") and self.familia.get("data_sorteio"):
            data_label = QLabel(f"📅 {self.familia.get('data_sorteio')}")
            data_label.setAlignment(Qt.AlignCenter)
            data_label.setStyleSheet("""
                QLabel {
                    color: #757575;
                    font-size: 12px;
                }
            """)
            self.layout.addWidget(data_label)
        
        # Action buttons
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(4)
        botoes_layout.setContentsMargins(0, 0, 0, 0)
        
        editar_btn = QPushButton("✎")
        editar_btn.clicked.connect(lambda: self.edit_clicked.emit(self.familia))
        editar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
                min-width: 32px;
                max-width: 32px;
                font-family: 'Segoe UI Symbol', 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        editar_btn.setFixedSize(32, 32)
        
        excluir_btn = QPushButton("🗑️")
        excluir_btn.clicked.connect(lambda: self.delete_clicked.emit(self.familia))
        excluir_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF5350;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-width: 32px;
                max-width: 32px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        excluir_btn.setFixedSize(32, 32)
        
        botoes_container = QWidget()
        botoes_container.setLayout(botoes_layout)
        botoes_layout.addWidget(editar_btn)
        botoes_layout.addWidget(excluir_btn)
        self.layout.addWidget(botoes_container, alignment=Qt.AlignCenter)

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
        self.loading_movie = QMovie("imagens/loading.gif")
        self.loading_movie.setScaledSize(QSize(300, 300))
        self.loading_label.setMovie(self.loading_movie)
        layout.addWidget(self.loading_label)
        
        # Set visibility after initializing all attributes
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