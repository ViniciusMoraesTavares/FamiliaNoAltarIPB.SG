from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QGroupBox, QFrame,
    QSpacerItem, QSizePolicy, QLineEdit, QGraphicsDropShadowEffect,
    QToolButton, QButtonGroup
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QMovie, QIntValidator
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, Signal, Property
import sys, os, random
from datetime import datetime

from src.adicionar_familia    import JanelaAdicionarFamilia
from src.janela_confirmacao    import JanelaConfirmacao
from src.filtro_familias       import nao_sorteadas, sorteadas, buscar
from src.data_manager import DataManager
from src.widgets import (
    NotificationWidget, AutoSaveBanner, LoadingOverlay,
    FamilyCard, SearchBar, FilterButton, TitleLabel, FullscreenImageViewer
)
from src.styles import AppStyles

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

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
        
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_movie = QMovie(os.path.join(BASE_PATH, "imagens", "loading.gif"))
        self.spinner_movie.setScaledSize(QSize(50, 50))
        self.spinner_label.setMovie(self.spinner_movie)
        layout.addWidget(self.spinner_label)
        
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
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        icon_label = QLabel("💾")
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
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
        
        spinner = QLabel("⌛")
        spinner.setFont(QFont("Segoe UI", 16))
        spinner.setAlignment(Qt.AlignCenter)
        spinner.setStyleSheet("color: #4CAF50;")
        layout.addWidget(spinner)
        
        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
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

        self.notification = NotificationWidget(self)
        self.auto_save_banner = AutoSaveBanner(self)
        self.loading_overlay = LoadingOverlay(self)
        self._batch_size = 40
        self._batch_index = 0
        self._cards = []
        self._familias_filtradas = []

        self.init_ui()
        self.showMaximized()

    def _on_nova_familia(self):
        self.filtro_atual = "todas"
        self.search_input.clear()
        self.data_manager.carregar_familias(force_reload=True)
        self.notification.show_message("Família adicionada com sucesso!", "success")
        self.atualizar_galeria()    

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.auto_save_banner)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

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

        titulo = TitleLabel("Família no Altar - IPB.SG", size=28)
        header_layout.addWidget(titulo)

        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)

        self.numero_input_panel = QLineEdit()
        self.numero_input_panel.setPlaceholderText("Número")
        self.numero_input_panel.setValidator(QIntValidator(1, 999, self))
        self.numero_input_panel.setFixedWidth(120)
        self.numero_input_panel.setStyleSheet(AppStyles.input_style())
        self.numero_input_panel.setVisible(False)
        self.numero_input_panel.setEnabled(False)
        self.numero_input_panel.returnPressed.connect(self._on_enter_panel_numero)
        botoes_layout.addWidget(self.numero_input_panel)

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

        for btn in [btn_adicionar, btn_sorteio, self.btn_fechar_sorteio, 
                   self.botao_finalizar, self.btn_resetar]:
            btn.setMinimumWidth(150)
            botoes_layout.addWidget(btn)

        botoes_layout.addStretch()
        header_layout.addLayout(botoes_layout)

        main_layout.addWidget(header)

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

        self.filter_buttons[0].setChecked(True)

        self.search_input = SearchBar()
        self.search_input.textChanged.connect(self.atualizar_busca)
        search_layout.addWidget(self.search_input)

        self.label_total = QLabel()
        self.label_total.setText(f"Total de Famílias: {len(self.data_manager.carregar_familias())}")
        self.label_total.setStyleSheet("font-size: 14px; color: #616161; font-weight: bold;")
        search_layout.addWidget(self.label_total)

        content_layout.addWidget(search_container)

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
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        main_layout.addWidget(content_widget)

        self.notification.setParent(self)
        self.notification.move(30, self.height() - 80)

        self.loading_overlay.setParent(self)
        
        self.atualizar_galeria()

    def resizeEvent(self, event):
        super().resizeEvent(event)
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

        self._cards = []
        self._familias_filtradas = familias
        self._batch_index = 0
        self._grid_layout = layout_grade
        self.scroll_area.setWidget(container)
        self.render_next_batch()
        self.verificar_reset_necessario()
        self.label_total.setText(f"Total de Famílias: {len(self.data_manager.carregar_familias())}")
        self.hideLoading()

    def render_next_batch(self):
        start = self._batch_index
        end = min(start + self._batch_size, len(self._familias_filtradas))
        for i in range(start, end):
            familia = self._familias_filtradas[i]
            card = FamilyCard(familia)
            card.edit_clicked.connect(self.abrir_edicao_familia)
            card.delete_clicked.connect(self.excluir_familia)
            card.image_clicked.connect(self.exibir_imagem_fullscreen)
            self._grid_layout.addWidget(card, i // 4, i % 4)
            self._cards.append(card)
        self._batch_index = end
        if len(self._familias_filtradas) < 4:
            self._grid_layout.setRowStretch(1, 1)

    def on_scroll(self):
        vp = self.scroll_area.viewport().rect()
        for card in self._cards:
            try:
                card.ensure_image_loaded(vp)
            except Exception:
                pass
        sb = self.scroll_area.verticalScrollBar()
        if sb.value() >= sb.maximum() - 50:
            if self._batch_index < len(self._familias_filtradas):
                self.render_next_batch()

    def exibir_imagem_fullscreen(self, imagem_url):
        fullscreen_widget = FullscreenImageViewer(imagem_url)
        fullscreen_widget.show()  

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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

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

        botoes_container = QWidget()
        botoes_container.setLayout(botoes_layout)
        botoes_layout.addWidget(editar_btn)
        botoes_layout.addWidget(excluir_btn)
        layout.addWidget(botoes_container, alignment=Qt.AlignCenter)

        return card

    def abrir_sorteio(self):
        from src.sorteio_tela import JanelaSorteio
        if self.janela_sorteio and self.janela_sorteio.isVisible():
            self.janela_sorteio.raise_()
            return

        self.janela_sorteio = JanelaSorteio()
        self.janela_sorteio.sorteioRealizado.connect(self.on_sorteio_realizado)
        self.janela_sorteio.ready.connect(self._on_sorteio_ready)
        
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
            self.numero_input_panel.clear()
            self.numero_input_panel.setVisible(False)
            self.numero_input_panel.setEnabled(False)

    def armazenar_sorteio_temporario(self, numero):
        self.numero_sorteado = numero
    
    def on_sorteio_realizado(self, numero):
        self.numero_sorteado = numero
        self.botao_finalizar.setEnabled(True)

    def _on_sorteio_ready(self):
        self.numero_input_panel.setEnabled(True)
        self.numero_input_panel.setVisible(True)
        self.numero_input_panel.setFocus()
        self.notification.show_message("Pronto para digitar o número", "info")

    def _on_enter_panel_numero(self):
        texto = self.numero_input_panel.text().strip()
        if not texto:
            self.notification.show_message("Digite um número válido.", "error")
            return
        if not self.janela_sorteio or not self.janela_sorteio.isVisible():
            self.notification.show_message("Abra a tela de sorteio primeiro.", "error")
            return
        try:
            self.janela_sorteio.mostrar_familia_por_numero(texto)
        except Exception as e:
            self.notification.show_message(f"Erro ao processar número: {str(e)}", "error")

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
                        self.numero_input_panel.clear()
                        self.numero_input_panel.setVisible(False)
                        self.numero_input_panel.setEnabled(False)

                    msg = f"Família {familia_sorteada['nome']} sorteada com sucesso!"
                    dlg = JanelaConfirmacao("", parent=self, info_text=msg)
                    dlg.exec()
                    
                    QTimer.singleShot(100, self.atualizar_galeria)
                    self.auto_save_banner.show_saved()
                else:
                    self.notification.show_message("Erro ao salvar sorteio", "error")
            else:
                self.notification.show_message("Erro ao salvar famílias", "error")

        self.hideLoading()

    def abrir_edicao_familia(self, familia):
        def callback_atualizacao():
            self.data_manager.carregar_familias(force_reload=True)
            self.atualizar_galeria()
            
        from src.editar_familia import JanelaEditarFamilia
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
        ok = self.data_manager.excluir_familia(familia["numero"])
        if ok:
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
