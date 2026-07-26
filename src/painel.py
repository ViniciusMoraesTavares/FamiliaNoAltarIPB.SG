from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QGroupBox, QFrame,
    QSpacerItem, QSizePolicy, QLineEdit, QGraphicsDropShadowEffect,
    QToolButton, QButtonGroup, QProgressBar
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QMovie, QIntValidator
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, Signal, Property
import sys, os, random
from datetime import datetime

from src.adicionar_familia    import JanelaAdicionarFamilia
from src.janela_confirmacao    import JanelaConfirmacao
from src.delete_confirm_dialog import DeleteConfirmDialog
from src.filtro_familias       import nao_sorteadas, sorteadas, buscar
from src.data_manager import DataManager
from src.numeros_impressao_dialog import NumerosImpressaoDialog
from src.widgets import (
    NotificationWidget, AutoSaveBanner, LoadingOverlay,
    SearchBar, FilterButton, TitleLabel, FullscreenImageViewer, PhotoViewer
)
from src.styles import AppStyles
from src.version import APP_VERSION
from src.icon import apply_windows_app_user_model_id, get_app_icon

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
        try:
            icon = get_app_icon()
            if not icon.isNull():
                self.setWindowIcon(icon)
        except Exception:
            pass
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
            Qt.WindowTitleHint |
            Qt.WindowSystemMenuHint |
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
        self._batch_size = 20
        self._batch_index = 0
        self._cards = []
        self._familias_filtradas = []
        self._batch_total = 0
        self._batch_errors = 0
        self._load_generation = 0
        self._gallery_container = None
        self._gallery_layout = None
        self._gallery_placeholder = None

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

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 16, 30, 16)

        titulo = TitleLabel("Painel — Família no Altar", size=26)
        header_layout.addWidget(titulo)

        # Removido bloco de botões do topo; controles estarão no menu lateral

        main_layout.addWidget(header)

        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame { background-color: #FAFAFA; border-right: 1px solid #E0E0E0; }
            QPushButton {
                text-align: left;
                padding: 12px 16px;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-weight: 600;
                color: #424242;
                background-color: white;
                margin: 8px;
            }
            QPushButton:hover { background-color: #F5F5F5; }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        btn_nav_sorteio = QPushButton("Abrir sorteio")
        btn_nav_sorteio.setStyleSheet("QPushButton { background-color: #2c4b23; color: white; border: none; border-radius: 10px; } QPushButton:hover { background-color: #243f1d; }")
        btn_nav_cadastro = QPushButton("Novo cadastro")
        btn_nav_sorteio.clicked.connect(self.abrir_sorteio)
        btn_nav_cadastro.clicked.connect(self.janela_adicionar.show)
        sidebar_layout.addWidget(btn_nav_sorteio)
        sidebar_layout.addWidget(btn_nav_cadastro)
        # Controles do sorteio (visíveis apenas quando a tela de sorteio estiver ativa)
        controls_container = QFrame()
        controls_container.setStyleSheet("QFrame { background: transparent; }")
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        controls_layout.setSpacing(8)

        numero_row = QHBoxLayout()
        numero_row.setContentsMargins(0, 0, 0, 0)
        numero_row.setSpacing(8)
        self.numero_input_panel = QLineEdit()
        self.numero_input_panel.setPlaceholderText("Número")
        self.numero_input_panel.setValidator(QIntValidator(1, 999, self))
        self.numero_input_panel.setMaxLength(3)
        self.numero_input_panel.setFixedWidth(100)
        self.numero_input_panel.setStyleSheet(AppStyles.input_style())
        self.numero_input_panel.setVisible(False)
        self.numero_input_panel.setEnabled(False)
        self.numero_input_panel.returnPressed.connect(self._on_enter_panel_numero)
        self.btn_confirmar_sidebar = QPushButton("Sortear")
        self.btn_confirmar_sidebar.setStyleSheet("QPushButton { background-color: #2c4b23; color: white; padding: 8px 12px; border-radius: 6px; } QPushButton:disabled { background-color: #9fb38f; }")
        self.btn_confirmar_sidebar.setEnabled(False)
        self.btn_confirmar_sidebar.clicked.connect(self._on_click_sorteio_botao)
        numero_row.addWidget(self.numero_input_panel)
        numero_row.addWidget(self.btn_confirmar_sidebar)

        self.btn_fechar_sorteio = QPushButton("Fechar Sorteio")
        self.btn_fechar_sorteio.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; padding: 8px 12px; border-radius: 6px; }")
        self.btn_fechar_sorteio.clicked.connect(self.fechar_sorteio)
        self.btn_fechar_sorteio.setVisible(False)

        controls_layout.addLayout(numero_row)
        controls_layout.addWidget(self.btn_fechar_sorteio)
        self.btn_resetar = QPushButton("Resetar Sorteio")
        self.btn_resetar.setStyleSheet("QPushButton { background-color: #FFB300; color: #1F2937; padding: 8px 12px; border-radius: 6px; } QPushButton:hover { background-color: #FFA000; }")
        self.btn_resetar.clicked.connect(self.resetar_sorteio_callback)
        self.btn_resetar.setVisible(False)
        controls_layout.addWidget(self.btn_resetar)
        controls_container.setVisible(True)

        sidebar_layout.addWidget(controls_container)
        sidebar_layout.addStretch()
        btn_imprimir_numeros = QPushButton("Imprimir números")
        btn_imprimir_numeros.clicked.connect(self._abrir_impressao_numeros)
        sidebar_layout.addWidget(btn_imprimir_numeros)
        btn_backup = QPushButton("Gerar backup")
        btn_backup.clicked.connect(self._on_backup_manual)
        sidebar_layout.addWidget(btn_backup)
        # Logo no canto inferior direito do menu lateral
        logo_label = QLabel()
        logo_label.setFixedSize(120, 120)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("margin: 0px; padding: 0px;")
        logo_abs = r"C:\Users\Myelin\OneDrive\Área de Trabalho\Vínicius\IPB_SG\Familia no altar\imagens\logo-ipbsg.png"
        logo_rel = os.path.join(BASE_PATH, "imagens", "logo-ipbsg.png")
        logo_path = logo_abs if os.path.exists(logo_abs) else logo_rel
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pm)
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.setSpacing(0)
        logo_row.addStretch(1)
        logo_row.addWidget(logo_label, alignment=Qt.AlignRight | Qt.AlignBottom)
        sidebar_layout.addLayout(logo_row)
        self._sidebar_controls = controls_container

        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(20)

        search_container = QFrame()
        search_container.setStyleSheet("QFrame { background-color: #F5F5F5; border-radius: 12px; }")
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
        self.label_total.setText("Preparando famílias...")
        self.label_total.setStyleSheet("font-size: 14px; color: #616161; font-weight: bold;")
        search_layout.addWidget(self.label_total)

        right_layout.addWidget(search_container)

        self.progress_card = QFrame()
        self.progress_card.setStyleSheet("""
            QFrame {
                background-color: #F8FAF8;
                border: 1px solid #DDE6D9;
                border-radius: 16px;
            }
            QLabel#progressTitle {
                color: #1F2937;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#progressSubtitle {
                color: #6B7280;
                font-size: 12px;
            }
            QLabel#progressPercent {
                color: #2c4b23;
                font-size: 22px;
                font-weight: 800;
            }
            QProgressBar {
                min-height: 12px;
                max-height: 12px;
                border: none;
                border-radius: 6px;
                background-color: #E5E7EB;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background-color: #2c4b23;
            }
        """)
        progress_layout = QVBoxLayout(self.progress_card)
        progress_layout.setContentsMargins(18, 16, 18, 16)
        progress_layout.setSpacing(10)
        progress_header = QHBoxLayout()
        progress_header.setContentsMargins(0, 0, 0, 0)
        progress_header.setSpacing(12)
        progress_texts = QVBoxLayout()
        progress_texts.setContentsMargins(0, 0, 0, 0)
        progress_texts.setSpacing(2)
        self.progress_title = QLabel("Carregando famílias")
        self.progress_title.setObjectName("progressTitle")
        self.progress_subtitle = QLabel("A interface já está pronta. Os registros serão exibidos gradualmente.")
        self.progress_subtitle.setObjectName("progressSubtitle")
        self.progress_subtitle.setWordWrap(True)
        progress_texts.addWidget(self.progress_title)
        progress_texts.addWidget(self.progress_subtitle)
        progress_header.addLayout(progress_texts, 1)
        self.progress_percent = QLabel("0%")
        self.progress_percent.setObjectName("progressPercent")
        progress_header.addWidget(self.progress_percent, 0, Qt.AlignRight | Qt.AlignVCenter)
        progress_layout.addLayout(progress_header)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.progress_card)

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
        right_layout.addWidget(self.scroll_area)
        self._build_empty_gallery("Aguardando dados...")

        page_layout.addWidget(sidebar)
        page_layout.addWidget(right_content)
        content_layout.addLayout(page_layout)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        main_layout.addWidget(content_widget)

        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 10, 30, 10)
        footer_layout.setSpacing(0)
        footer_label = QLabel(f"Família no Altar • versão {APP_VERSION}")
        footer_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch(1)
        main_layout.addWidget(footer)

        self.notification.setParent(self)
        self.notification.move(30, self.height() - 80)

        self.loading_overlay.setParent(self)

        QTimer.singleShot(0, self.atualizar_galeria)

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
            if hasattr(self, "btn_confirmar_sidebar") and self.btn_confirmar_sidebar:
                self.btn_confirmar_sidebar.setEnabled(False)
                self.btn_confirmar_sidebar.setText("Sortear")
            self.numero_sorteado = None
            self.notification.show_message(
                "Sorteio resetado com sucesso! Novos números foram distribuídos.",
                "success"
            )
            self.auto_save_banner.show_saved()
        else:
            self.notification.show_message("Erro ao resetar sorteio", "error")
        
        self.hideLoading()

    def _on_backup_manual(self):
        self.showLoading()
        QTimer.singleShot(100, self._on_backup_manual_impl)

    def _on_backup_manual_impl(self):
        ok = False
        try:
            ok = self.data_manager.criar_backup_manual(APP_VERSION)
        except Exception:
            ok = False
        self.hideLoading()
        if ok:
            msg = "Backup criado com sucesso em %APPDATA%/FamiliaNoAltar/backups"
            dlg = JanelaConfirmacao("", parent=self, info_text=msg)
            dlg.exec()
        else:
            self.notification.show_message("Falha ao criar backup", "error")

    def _abrir_impressao_numeros(self):
        familias = nao_sorteadas(self.data_manager.carregar_familias())
        try:
            familias = sorted(familias, key=lambda f: int(f.get("numero", 0)))
        except Exception:
            familias = sorted(familias, key=lambda f: str(f.get("numero", "")))

        numeros = []
        for familia in familias:
            try:
                numeros.append(int(familia.get("numero")))
            except Exception:
                continue

        if not numeros:
            self.notification.show_message(
                "Não há famílias aguardando sorteio para imprimir.",
                "info",
            )
            return

        dialog = NumerosImpressaoDialog(numeros, self)
        dialog.exec()

    def atualizar_filtro(self, filtro):
        self.filtro_atual = filtro
        self.atualizar_galeria()

    def atualizar_busca(self, texto):
        self.termo_pesquisa = texto
        self.atualizar_galeria()

    def _formatar_total_familias(self, total, filtro=None):
        filtro = filtro or self.filtro_atual
        if filtro == "sorteadas":
            return f"{total} famílias sorteadas"
        if filtro == "nao_sorteadas":
            return f"{total} famílias aguardando sorteio"
        return f"{total} famílias"

    def _total_por_filtro(self, familias):
        if self.filtro_atual == "sorteadas":
            return len(sorteadas(familias))
        if self.filtro_atual == "nao_sorteadas":
            return len(nao_sorteadas(familias))
        return len(familias)

    def atualizar_galeria(self):
        self._load_generation += 1
        generation = self._load_generation
        self._batch_index = 0
        self._batch_errors = 0
        self._cards = []
        self._familias_filtradas = []
        self._batch_total = 0
        self._set_progress_state(
            visible=True,
            title="Carregando famílias",
            subtitle="A interface já está pronta. Os registros serão exibidos gradualmente.",
            percent=0,
        )
        self.label_total.setText("Carregando famílias...")
        self._build_empty_gallery("Preparando registros...")
        QTimer.singleShot(0, lambda: self._preparar_carregamento_galeria(generation))

    def _preparar_carregamento_galeria(self, generation):
        if generation != self._load_generation:
            return

        try:
            familias_base = self.data_manager.carregar_familias()
        except Exception as exc:
            self._set_progress_state(
                visible=True,
                title="Falha ao carregar famílias",
                subtitle="A interface continua disponível. Tente novamente em alguns instantes.",
                percent=0,
            )
            self.label_total.setText("Falha ao carregar famílias")
            self._build_empty_gallery("Não foi possível carregar os registros.")
            self.notification.show_message(f"Falha ao carregar famílias: {exc}", "error")
            return

        familias = list(familias_base)
        if self.filtro_atual == "nao_sorteadas":
            familias = nao_sorteadas(familias)
        elif self.filtro_atual == "sorteadas":
            familias = sorteadas(familias)

        familias = buscar(familias, self.termo_pesquisa)
        try:
            familias = sorted(familias, key=lambda f: int(f.get("numero", 0)))
        except Exception:
            familias = sorted(familias, key=lambda f: str(f.get("numero", "")))

        self._familias_filtradas = familias
        self._batch_total = len(familias)
        self.verificar_reset_necessario()
        total_base = len(familias_base)
        total_filtro = self._total_por_filtro(familias_base)

        if not familias:
            texto_vazio = "Nenhuma família encontrada para o filtro atual."
            self._build_empty_gallery(texto_vazio)
            self.label_total.setText(self._formatar_total_familias(total_filtro))
            self._set_progress_state(
                visible=bool(total_base),
                title="Carregamento concluído",
                subtitle="Nenhum registro corresponde ao filtro informado." if total_base else "Cadastre a primeira família para começar.",
                percent=100,
            )
            if total_base:
                QTimer.singleShot(1500, lambda: self._hide_progress_if_idle(generation))
            return

        self.label_total.setText(self._formatar_total_familias(total_filtro))
        self._build_empty_gallery("Carregando primeiros registros...")
        self._processar_proximo_lote(generation)

    def _processar_proximo_lote(self, generation):
        if generation != self._load_generation:
            return

        inicio = self._batch_index
        fim = min(inicio + self._batch_size, self._batch_total)
        lote = self._familias_filtradas[inicio:fim]

        for familia in lote:
            try:
                if self._gallery_placeholder is not None:
                    self._gallery_layout.removeWidget(self._gallery_placeholder)
                    self._gallery_placeholder.hide()
                    self._gallery_placeholder.deleteLater()
                    self._gallery_placeholder = None
                item = self._criar_item_lista(familia)
                self._gallery_layout.insertWidget(self._gallery_layout.count() - 1, item)
                self._cards.append(item)
            except Exception:
                self._batch_errors += 1

        self._batch_index = fim
        percentual = 100 if self._batch_total == 0 else int((self._batch_index / self._batch_total) * 100)
        restante = max(self._batch_total - self._batch_index, 0)
        self._set_progress_state(
            visible=True,
            title="Carregando famílias",
            subtitle=f"{self._batch_index} registros adicionados. Restam {restante}.",
            percent=percentual,
        )

        if self._batch_index < self._batch_total:
            QTimer.singleShot(12, lambda: self._processar_proximo_lote(generation))
            return

        mensagem_final = f"{self._batch_total} famílias carregadas com sucesso."
        if self._batch_errors:
            mensagem_final = f"{self._batch_total - self._batch_errors} famílias carregadas. {self._batch_errors} itens apresentaram falha."
            self.notification.show_message(
                "Alguns registros não puderam ser exibidos, mas o sistema continua operacional.",
                "error",
            )

        self._set_progress_state(
            visible=True,
            title="Carregamento concluído",
            subtitle=mensagem_final,
            percent=100,
        )
        QTimer.singleShot(1800, lambda: self._hide_progress_if_idle(generation))

    def _build_empty_gallery(self, empty_message=""):
        anterior = self.scroll_area.takeWidget()
        if anterior is not None:
            anterior.deleteLater()

        self._gallery_container = QWidget()
        self._gallery_container.setStyleSheet("background-color: transparent;")
        self._gallery_layout = QVBoxLayout(self._gallery_container)
        self._gallery_layout.setContentsMargins(0, 0, 0, 0)
        self._gallery_layout.setSpacing(8)

        if empty_message:
            self._gallery_placeholder = QLabel(empty_message)
            self._gallery_placeholder.setAlignment(Qt.AlignCenter)
            self._gallery_placeholder.setStyleSheet(
                "QLabel { color: #6B7280; font-size: 14px; padding: 28px; "
                "background-color: #F9FAFB; border: 1px dashed #D1D5DB; border-radius: 12px; }"
            )
            self._gallery_layout.addWidget(self._gallery_placeholder)
        else:
            self._gallery_placeholder = None

        self._gallery_layout.addStretch()
        self.scroll_area.setWidget(self._gallery_container)

    def _set_progress_state(self, visible, title, subtitle, percent):
        self.progress_card.setVisible(visible)
        self.progress_title.setText(title)
        self.progress_subtitle.setText(subtitle)
        self.progress_bar.setValue(max(0, min(100, int(percent))))
        self.progress_percent.setText(f"{max(0, min(100, int(percent)))}%")

    def _hide_progress_if_idle(self, generation):
        if generation == self._load_generation and self._batch_index >= self._batch_total:
            self.progress_card.hide()

    def on_scroll(self):
        pass

    def exibir_imagem_fullscreen(self, imagem_url):
        if not imagem_url:
            return
        abs_path = self.data_manager._resolve_photo_abs(imagem_url) if imagem_url else ""
        if abs_path and os.path.exists(abs_path):
            pix = QPixmap(abs_path)
            viewer = PhotoViewer(pix, self)
            viewer.exec_()

    def verificar_reset_necessario(self):
        familias = self.data_manager.carregar_familias()
        todas = all(f.get("sorteado", False) for f in familias)
        if hasattr(self, "btn_resetar") and self.btn_resetar:
            self.btn_resetar.setVisible(todas)

    def _criar_item_lista(self, familia):
        item = QFrame()
        item.setStyleSheet("QFrame { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; }")
        h = QHBoxLayout(item)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(12)
        numero = QLabel(f"{familia.get('numero', '-')}")
        numero.setStyleSheet("QLabel { font-size: 16px; font-weight: 700; color: #212121; }")
        nome = QLabel(f"{familia.get('nome','')}")
        nome.setStyleSheet("QLabel { font-size: 16px; font-weight: 600; color: #1F2937; }")
        nome.mousePressEvent = lambda e, f=familia: self._abrir_modal_foto(f)
        h.addWidget(numero, 0)
        h.addWidget(nome, 1)
        _sorteada = familia.get("sorteado")
        status_icon = QLabel("✓" if _sorteada else "⌛")
        status_icon.setToolTip("Família sorteada" if _sorteada else "Família aguardando sorteio")
        status_icon.setStyleSheet("QLabel { color: %s; font-size: 20px; font-weight: 700; }" % ("#2c4b23" if _sorteada else "#757575"))
        h.addWidget(status_icon, 0)
        editar = QPushButton("Editar")
        editar.setStyleSheet("QPushButton { background-color: #2c4b23; color: white; padding: 6px 12px; border-radius: 6px; } QPushButton:hover { background-color: #243f1d; }")
        editar.clicked.connect(lambda: self.abrir_edicao_familia(familia))
        excluir = QPushButton("Excluir")
        excluir.setStyleSheet("QPushButton { background-color: #EF5350; color: white; padding: 6px 12px; border-radius: 6px; } QPushButton:hover { background-color: #E53935; }")
        excluir.clicked.connect(lambda: self.excluir_familia(familia))
        h.addWidget(editar, 0)
        h.addWidget(excluir, 0)
        return item

    def _abrir_modal_foto(self, familia):
        caminho = familia.get("foto", "")
        if not caminho:
            return
        abs_path = self.data_manager._resolve_photo_abs(caminho)
        if abs_path and os.path.exists(abs_path):
            pix = QPixmap(abs_path)
            viewer = PhotoViewer(pix, self)
            viewer.exec_()

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
        
        self.btn_fechar_sorteio.setVisible(True)

    def fechar_sorteio(self):
        if self.janela_sorteio:
            self.janela_sorteio.close()
            self.janela_sorteio = None
            self.btn_fechar_sorteio.setVisible(False)
            self.numero_sorteado = None
            self.btn_confirmar_sidebar.setEnabled(False)
            self.btn_confirmar_sidebar.setText("Sortear")
            self.numero_input_panel.clear()
            self.numero_input_panel.setVisible(False)
            self.numero_input_panel.setEnabled(False)

    def armazenar_sorteio_temporario(self, numero):
        self.numero_sorteado = numero
    
    def on_sorteio_realizado(self, numero):
        self.numero_sorteado = numero
        self.btn_confirmar_sidebar.setEnabled(True)
        self.btn_confirmar_sidebar.setText("Confirmar")

    def _on_sorteio_ready(self):
        self.numero_input_panel.setEnabled(True)
        self.numero_input_panel.setVisible(True)
        self.numero_input_panel.setFocus()
        self.notification.show_message("Pronto para digitar o número", "info")
        self.btn_fechar_sorteio.setVisible(True)
        self.btn_confirmar_sidebar.setEnabled(True)
        self.btn_confirmar_sidebar.setText("Sortear")

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

    def _on_click_sorteio_botao(self):
        if not self.numero_sorteado:
            # realiza o sorteio (mesmo comportamento do Enter)
            self._on_enter_panel_numero()
        else:
            # confirma/registrar sorteio
            self.finalizar_sorteio_panel()

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
                    self.btn_confirmar_sidebar.setEnabled(False)
                    self.btn_fechar_sorteio.setVisible(False)
                    self.btn_confirmar_sidebar.setText("Sortear")

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
            try:
                ultimo = self.data_manager.carregar_ultimo_sorteio()
                if self.janela_sorteio and self.janela_sorteio.isVisible():
                    self.janela_sorteio.atualizar_ultimo_sorteado()
                    if ultimo:
                        self.janela_sorteio.mostrar_familia_por_numero(str(ultimo))
            except Exception:
                pass
            
        from src.editar_familia import JanelaEditarFamilia
        self.janela_edicao = JanelaEditarFamilia(familia, callback_atualizacao)
        self.janela_edicao.show()

    def excluir_familia(self, familia):
        texto = f"Tem certeza que deseja excluir a família '{familia['nome']}'?"
        dlg = DeleteConfirmDialog(texto, parent=self)
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
    apply_windows_app_user_model_id()
    app = QApplication(sys.argv)
    try:
        icon = get_app_icon()
        if not icon.isNull():
            app.setWindowIcon(icon)
    except Exception:
        pass
    painel = PainelPrincipal()
    sys.exit(app.exec())
