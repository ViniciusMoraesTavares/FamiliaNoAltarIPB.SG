from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QGroupBox, QFrame,
    QSpacerItem, QSizePolicy, QLineEdit, QGraphicsDropShadowEffect,
    QToolButton, QButtonGroup
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QMovie
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, Signal, Property
import sys, os, random
from datetime import datetime

from src.adicionar_familia    import JanelaAdicionarFamilia
from src.sorteio_tela          import JanelaSorteio
from src.editar_familia        import JanelaEditarFamilia
from src.janela_confirmacao    import JanelaConfirmacao
from src.utils                 import carregar_familias, salvar_familias
from src.filtro_familias       import nao_sorteadas, sorteadas, buscar
from src.utils_familias import contar_familias
from src.utils_sorteio import salvar_sorteio
from src.resetar import resetar_sorteio
from src.data_manager import DataManager
from src.widgets import (
    NotificationWidget, AutoSaveBanner, LoadingOverlay,
    FamilyCard, SearchBar, FilterButton, TitleLabel
)
from src.styles import AppStyles


class LoadingSpinner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Loading animation
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_movie = QMovie("imagens/loading.gif")
        self.spinner_movie.setScaledSize(QSize(50, 50))
        self.spinner_label.setMovie(self.spinner_movie)
        layout.addWidget(self.spinner_label)
        
        # Loading text
        text_label = QLabel("Carregando...")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("""
            QLabel {
                color: #616161;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(text_label)
        
        self.hide()
        
    def showEvent(self, event):
        super().showEvent(event)
        self.spinner_movie.start()
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.spinner_movie.stop()

class JanelaSalvamento(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Ícone de salvamento
        icon_label = QLabel("💾")
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Mensagem
        msg_label = QLabel("Salvando todas as alterações...")
        msg_label.setStyleSheet("""
            QLabel {
                color: #424242;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label)
        
        # Loading spinner
        spinner = QLabel("⌛")
        spinner.setFont(QFont("Segoe UI", 16))
        spinner.setAlignment(Qt.AlignCenter)
        spinner.setStyleSheet("color: #4CAF50;")
        layout.addWidget(spinner)
        
        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
        # Centralizar a janela no pai
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
            self.move(x, y)

class PainelPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Família no Altar - Painel")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: #FAFAFA;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowMinMaxButtonsHint |
            Qt.WindowCloseButtonHint
        )

        self.filtro_atual = "todas"
        self.termo_pesquisa = ""
        self.data_manager = DataManager()

        self.janela_adicionar = JanelaAdicionarFamilia()
        self.janela_adicionar.familia_adicionada.connect(self._on_nova_familia)
        self.janela_sorteio = None
        self.numero_sorteado = None

        # Initialize widgets
        self.notification = NotificationWidget(self)
        self.auto_save_banner = AutoSaveBanner(self)
        self.loading_overlay = LoadingOverlay(self)

        self.init_ui()
        self.showMaximized()

    def _on_nova_familia(self):
        self.filtro_atual = "todas"
        self.search_input.clear()
        # Força recarregar os dados
        self.data_manager.carregar_familias(force_reload=True)
        self.notification.show_message("Família adicionada com sucesso!", "success")
        self.atualizar_galeria()    

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add auto-save banner at the top
        main_layout.addWidget(self.auto_save_banner)

        # Content container with padding
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Header with shadow
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        header.setGraphicsEffect(AppStyles.get_shadow_effect())

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)

        # Title
        titulo = TitleLabel("Família no Altar - IPB.SG", size=28)
        header_layout.addWidget(titulo)

        # Action buttons
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)

        # Create action buttons
        btn_adicionar = QPushButton("➕ Adicionar Família")
        btn_adicionar.clicked.connect(self.janela_adicionar.show)
        btn_adicionar.setStyleSheet(AppStyles.button_style())

        btn_sorteio = QPushButton("🎲 Iniciar Sorteio")
        btn_sorteio.clicked.connect(self.abrir_sorteio)
        btn_sorteio.setStyleSheet(AppStyles.button_style())

        self.btn_fechar_sorteio = QPushButton("❌ Fechar Sorteio")
        self.btn_fechar_sorteio.clicked.connect(self.fechar_sorteio)
        self.btn_fechar_sorteio.setStyleSheet(AppStyles.button_style())
        self.btn_fechar_sorteio.setVisible(False)

        self.botao_finalizar = QPushButton("✅ Finalizar Sorteio")
        self.botao_finalizar.clicked.connect(self.finalizar_sorteio_panel)
        self.botao_finalizar.setStyleSheet(AppStyles.button_style())
        self.botao_finalizar.setEnabled(False)

        self.btn_resetar = QPushButton("🔄 Resetar Sorteio")
        self.btn_resetar.clicked.connect(self.resetar_sorteio_callback)
        self.btn_resetar.setStyleSheet(AppStyles.button_style())
        self.btn_resetar.setVisible(False)

        # Add buttons to layout
        for btn in [btn_adicionar, btn_sorteio, self.btn_fechar_sorteio, 
                   self.botao_finalizar, self.btn_resetar]:
            btn.setMinimumWidth(150)
            botoes_layout.addWidget(btn)

        botoes_layout.addStretch()
        header_layout.addLayout(botoes_layout)

        main_layout.addWidget(header)

        # Search and filters section
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 12px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 15, 20, 15)
        search_layout.setSpacing(15)

        # Filter buttons
        self.filter_buttons = []
        filter_group = QButtonGroup(self)
        filter_group.setExclusive(True)
        
        for label, filter_name in [
            ("Todas", "todas"),
            ("Não Sorteadas", "nao_sorteadas"),
            ("Sorteadas", "sorteadas")
        ]:
            btn = FilterButton(label)
            btn.clicked.connect(lambda checked, f=filter_name: self.atualizar_filtro(f))
            filter_group.addButton(btn)
            self.filter_buttons.append(btn)
            search_layout.addWidget(btn)

        # Set the "Todas" button as checked by default
        self.filter_buttons[0].setChecked(True)

        # Search bar
        self.search_input = SearchBar()
        self.search_input.textChanged.connect(self.atualizar_busca)
        search_layout.addWidget(self.search_input)

        # Total families label
        self.label_total = QLabel()
        self.label_total.setText(f"Total de Famílias: {contar_familias()}")
        self.label_total.setStyleSheet("font-size: 14px; color: #616161; font-weight: bold;")
        search_layout.addWidget(self.label_total)

        content_layout.addWidget(search_container)

        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        content_layout.addWidget(self.scroll_area)

        main_layout.addWidget(content_widget)

        # Add notification widget (it will be hidden by default)
        self.notification.setParent(self)
        self.notification.move(30, self.height() - 80)

        # Add loading overlay
        self.loading_overlay.setParent(self)
        
        self.atualizar_galeria()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update notification and loading spinner positions
        self.notification.move(30, self.height() - 80)
        self.loading_overlay.resize(self.size())

    def estilo_botao_principal(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #F1F8E9;
            }
            QPushButton:focus {
                outline: none;
            }
        """

    def resetar_sorteio_callback(self):
        self.showLoading()
        self.auto_save_banner.show_saving()
        
        if self.data_manager.resetar_sorteio():
            self.atualizar_galeria()
            self.botao_finalizar.setEnabled(False)
            self.numero_sorteado = None
            self.notification.show_message(
                "Sorteio resetado com sucesso! Novos números foram distribuídos.",
                "success"
            )
            self.auto_save_banner.show_saved()
        else:
            self.notification.show_message("Erro ao resetar sorteio", "error")
        
        self.hideLoading()

    def atualizar_filtro(self, filtro):
        self.filtro_atual = filtro
        self.atualizar_galeria()

    def atualizar_busca(self, texto):
        self.termo_pesquisa = texto
        self.atualizar_galeria()

    def atualizar_galeria(self):
        self.showLoading()
        QTimer.singleShot(100, self._atualizar_galeria_impl)

    def _atualizar_galeria_impl(self):
        familias = self.data_manager.carregar_familias()

        if self.filtro_atual == "nao_sorteadas":
            familias = nao_sorteadas(familias)
        elif self.filtro_atual == "sorteadas":
            familias = sorteadas(familias)

        familias = buscar(familias, self.termo_pesquisa)

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout_grade = QGridLayout(container)
        layout_grade.setContentsMargins(10, 10, 10, 10)
        layout_grade.setSpacing(20)

        for i, familia in enumerate(familias):
            card = FamilyCard(familia)
            card.edit_clicked.connect(self.abrir_edicao_familia)
            card.delete_clicked.connect(self.excluir_familia)
            layout_grade.addWidget(card, i // 4, i % 4)

        # Add stretch to bottom if needed
        if len(familias) < 4:
            layout_grade.setRowStretch(1, 1)

        self.scroll_area.setWidget(container)
        self.verificar_reset_necessario()
        self.label_total.setText(f"Total de Famílias: {contar_familias()}")
        self.hideLoading()

    def verificar_reset_necessario(self):
        familias = self.data_manager.carregar_familias()
        todas = all(f.get("sorteado", False) for f in familias)
        self.btn_resetar.setVisible(todas)

    def criar_card_familia(self, familia):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Image container with rounded corners
        img_container = QFrame()
        img_container.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                min-height: 120px;
            }
        """)
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(0, 0, 0, 0)

        img_label = QLabel()
        img_label.setFixedSize(120, 120)
        img_label.setAlignment(Qt.AlignCenter)
        
        caminho = familia.get("foto", "")
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(pixmap)
            img_label.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                }
            """)
        else:
            img_label.setText("📷")
            img_label.setFont(QFont("Segoe UI", 40))
            img_label.setStyleSheet("""
                QLabel {
                    color: #9E9E9E;
                }
            """)

        img_layout.addWidget(img_label, alignment=Qt.AlignCenter)
        layout.addWidget(img_container)

        # Family info
        nome_label = QLabel(familia.get("nome", "Sem Nome"))
        nome_label.setAlignment(Qt.AlignCenter)
        nome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #212121;
            }
        """)
        layout.addWidget(nome_label)

        numero_label = QLabel(f"Número: {familia.get('numero', '-')}")
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 14px;
            }
        """)
        layout.addWidget(numero_label)

        # Status badge
        status_container = QFrame()
        status_container.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border-radius: 12px;
                padding: 5px;
            }
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 5, 10, 5)

        status = "Sorteado" if familia.get("sorteado") else "Aguardando"
        icon = "✓" if familia.get("sorteado") else "⏳"
        status_label = QLabel(f"{icon} {status}")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(
            "color: #2E7D32; font-weight: bold;" if familia.get("sorteado") 
            else "color: #757575; font-style: italic;"
        )
        status_layout.addWidget(status_label)
        layout.addWidget(status_container)

        if familia.get("sorteado") and familia.get("data_sorteio"):
            data_label = QLabel(f"📅 {familia.get('data_sorteio')}")
            data_label.setAlignment(Qt.AlignCenter)
            data_label.setStyleSheet("""
                QLabel {
                    color: #757575;
                    font-size: 12px;
                }
            """)
            layout.addWidget(data_label)

        # Action buttons
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(4)
        botoes_layout.setContentsMargins(0, 0, 0, 0)

        editar_btn = QPushButton("✏️")
        editar_btn.clicked.connect(lambda: self.abrir_edicao_familia(familia))
        editar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
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
                background-color: #43A047;
            }
        """)

        excluir_btn = QPushButton("🗑️")
        excluir_btn.clicked.connect(lambda: self.excluir_familia(familia))
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

        # Centralizar os botões
        botoes_container = QWidget()
        botoes_container.setLayout(botoes_layout)
        botoes_layout.addWidget(editar_btn)
        botoes_layout.addWidget(excluir_btn)
        layout.addWidget(botoes_container, alignment=Qt.AlignCenter)

        return card

    def abrir_sorteio(self):
        if self.janela_sorteio and self.janela_sorteio.isVisible():
            self.janela_sorteio.raise_()
            return

        self.janela_sorteio = JanelaSorteio()
        self.janela_sorteio.sorteioRealizado.connect(self.on_sorteio_realizado)
        
        # Primeiro mostra a janela e depois maximiza
        self.janela_sorteio.show()
        QTimer.singleShot(100, self.janela_sorteio.showFullScreen)
        
        self.botao_finalizar.setEnabled(True)
        self.btn_fechar_sorteio.setVisible(True)

    def fechar_sorteio(self):
        if self.janela_sorteio:
            self.janela_sorteio.close()
            self.janela_sorteio = None
            self.btn_fechar_sorteio.setVisible(False)
            self.numero_sorteado = None
            self.botao_finalizar.setEnabled(False)

    def armazenar_sorteio_temporario(self, numero):
        self.numero_sorteado = numero
    
    def on_sorteio_realizado(self, numero):
        self.numero_sorteado = numero
        self.botao_finalizar.setEnabled(True)

    def finalizar_sorteio_panel(self):
        if not self.numero_sorteado:
            return

        self.showLoading()
        self.auto_save_banner.show_saving()
        
        QTimer.singleShot(100, self._finalizar_sorteio_impl)

    def _finalizar_sorteio_impl(self):
        familias = self.data_manager.carregar_familias()
        familia_sorteada = next(
            (f for f in familias if str(f.get("numero")) == str(self.numero_sorteado)),
            None
        )

        if familia_sorteada:
            familia_sorteada["sorteado"] = True
            familia_sorteada["data_sorteio"] = datetime.now().strftime("%d/%m/%Y")

            if self.data_manager.salvar_familias(familias):
                if self.data_manager.salvar_sorteio(self.numero_sorteado):
                    self.numero_sorteado = None
                    self.botao_finalizar.setEnabled(False)
                    self.btn_fechar_sorteio.setVisible(False)

                    if self.janela_sorteio:
                        self.janela_sorteio.close()
                        self.janela_sorteio = None

                    # Mostrar janela de confirmação apenas com OK para o sorteio
                    msg = f"Família {familia_sorteada['nome']} sorteada com sucesso!"
                    dlg = JanelaConfirmacao("", parent=self, info_text=msg)
                    dlg.exec()
                    
                    # Forçar atualização da galeria após o diálogo
                    QTimer.singleShot(100, self.atualizar_galeria)
                    self.auto_save_banner.show_saved()
                else:
                    self.notification.show_message("Erro ao salvar sorteio", "error")
            else:
                self.notification.show_message("Erro ao salvar famílias", "error")

        self.hideLoading()

    def abrir_edicao_familia(self, familia):
        def callback_atualizacao():
            # Força recarregar os dados
            self.data_manager.carregar_familias(force_reload=True)
            self.atualizar_galeria()
            
        self.janela_edicao = JanelaEditarFamilia(familia, callback_atualizacao)
        self.janela_edicao.show()

    def excluir_familia(self, familia):
        texto = f"Tem certeza que deseja excluir a família '{familia['nome']}'?"
        dlg = JanelaConfirmacao(texto, parent=self)
        dlg.confirmado.connect(lambda: self._executar_exclusao(familia))
        dlg.show()

    def _executar_exclusao(self, familia):
        self.showLoading()
        self.auto_save_banner.show_saving()
        
        QTimer.singleShot(100, lambda: self._executar_exclusao_impl(familia))

    def _executar_exclusao_impl(self, familia):
        familias = self.data_manager.carregar_familias()
        familias = [f for f in familias if f["numero"] != familia["numero"]]
        
        if self.data_manager.salvar_familias(familias):
            self.notification.show_message(f"Família {familia['nome']} removida com sucesso!", "success")
            self.auto_save_banner.show_saved()
            self.atualizar_galeria()
        else:
            self.notification.show_message("Erro ao remover família", "error")
        
        self.hideLoading()

    def showLoading(self):
        self.loading_overlay.resize(self.size())
        self.loading_overlay.show()
        
    def hideLoading(self):
        self.loading_overlay.hide()

    def closeEvent(self, event):
        QApplication.quit()

def iniciar_painel():
    app = QApplication(sys.argv)
    painel = PainelPrincipal()
    sys.exit(app.exec())