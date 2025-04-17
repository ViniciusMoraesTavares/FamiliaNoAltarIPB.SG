from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QSize
import sys, os, random

from src.adicionar_familia import JanelaAdicionarFamilia
from src.sorteio_tela import JanelaSorteio
from src.utils import carregar_familias, salvar_familias
from src.editar_familia import JanelaEditarFamilia


class PainelPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Família no Altar - Painel")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.janela_adicionar = JanelaAdicionarFamilia()
        self.janela_sorteio = None
        self.numero_sorteado = None

        self.init_ui()
        self.showMaximized()

    def familia_adicionada_com_sucesso(self):
        self.atualizar_galeria()  # Atualiza a galeria após adicionar a família
        self.repaint()  # Força a atualização da interface imediatamente

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        titulo = QLabel("📊 Painel de Controle - Família no Altar")
        titulo.setFont(QFont("Arial", 28, QFont.Bold))
        titulo.setStyleSheet("color: #2E7D32;")
        layout.addWidget(titulo, alignment=Qt.AlignLeft)

        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(20)

        btn_adicionar = QPushButton("➕ Adicionar Família")
        btn_adicionar.clicked.connect(self.janela_adicionar.show)
        btn_adicionar.setStyleSheet(self.estilo_botao_principal())

        btn_sorteio = QPushButton("🎲 Iniciar Sorteio")
        btn_sorteio.clicked.connect(self.abrir_sorteio)
        btn_sorteio.setStyleSheet(self.estilo_botao_principal())

        self.botao_finalizar = QPushButton("✅ Finalizar Sorteio")
        self.botao_finalizar.clicked.connect(self.finalizar_sorteio_panel)
        self.botao_finalizar.setStyleSheet(self.estilo_botao_principal())
        self.botao_finalizar.setEnabled(False)

        self.btn_resetar = QPushButton("🔄 Resetar Sorteio")
        self.btn_resetar.setStyleSheet(self.estilo_botao_principal())
        self.btn_resetar.clicked.connect(self.resetar_sorteio)
        self.btn_resetar.setVisible(False)

        botoes_layout.addWidget(btn_adicionar)
        botoes_layout.addWidget(btn_sorteio)
        botoes_layout.addWidget(self.botao_finalizar)
        botoes_layout.addWidget(self.btn_resetar)

        layout.addLayout(botoes_layout)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        layout.addWidget(self.scroll_area)

        self.atualizar_galeria()
        self.setLayout(layout)

    def verificar_reset_necessario(self):
        familias = carregar_familias()
        todas_sorteadas = all(f.get("sorteado", False) for f in familias)
        self.btn_resetar.setVisible(todas_sorteadas)

    def resetar_sorteio(self):
        familias = carregar_familias()

        for f in familias:
            f["sorteado"] = False

        total = len(familias)
        numeros_aleatorios = list(range(1, total + 1))
        random.shuffle(numeros_aleatorios)

        for f, novo_numero in zip(familias, numeros_aleatorios):
            f["numero"] = novo_numero

        salvar_familias(familias)
        self.numero_sorteado = None
        self.botao_finalizar.setEnabled(False)
        self.atualizar_galeria()
        self.verificar_reset_necessario()

    def estilo_botao_principal(self):
        return """
            QPushButton {
                padding: 15px 25px;
                font-size: 18px;
                color: white;
                background-color: #388E3C;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #f0f0f0;
            }
        """

    def atualizar_galeria(self):
        familias = carregar_familias()
        grupo = QGroupBox("Famílias Cadastradas")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 20px;
                color: #2E7D32;
                margin-top: 10px;
            }
        """)
        layout_grade = QGridLayout()
        layout_grade.setSpacing(25)

        for i, f in enumerate(familias):
            card = self.criar_card_familia(f)
            layout_grade.addWidget(card, i // 4, i % 4)

        grupo.setLayout(layout_grade)
        self.scroll_area.setWidget(grupo)

        self.verificar_reset_necessario()

    def criar_card_familia(self, familia):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        img_label = QLabel()
        caminho = familia.get("foto", "")
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(pixmap)
        else:
            img_label.setText("📷")
            img_label.setFont(QFont("Arial", 40))

        img_label.setAlignment(Qt.AlignCenter)

        nome_label = QLabel(familia.get("nome", "Sem Nome"))
        nome_label.setAlignment(Qt.AlignCenter)
        nome_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #444;")

        numero_label = QLabel(f"🎟️ Número: {familia.get('numero', '-')}") 
        numero_label.setAlignment(Qt.AlignCenter)
        numero_label.setStyleSheet("color: #555; font-size: 14px;")

        status_label = QLabel("✅ Sorteado" if familia.get("sorteado") else "⏳ Aguardando")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: green;" if familia.get("sorteado") else "color: #888; font-style: italic;")

        editar_btn = QPushButton("✏️ Editar")
        editar_btn.setStyleSheet("""
            QPushButton {
                background-color: #81C784;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        editar_btn.clicked.connect(lambda: self.abrir_edicao_familia(familia))

        layout.addWidget(img_label)
        layout.addWidget(nome_label)
        layout.addWidget(numero_label)
        layout.addWidget(status_label)
        layout.addWidget(editar_btn)

        widget.setLayout(layout)
        widget.setStyleSheet("""
            background-color: #F1F8E9;
            border: 1px solid #C8E6C9;
            border-radius: 10px;
        """)
        return widget

    def abrir_sorteio(self):
        if self.janela_sorteio and self.janela_sorteio.isVisible():
            self.janela_sorteio.raise_()
            return

        self.janela_sorteio = JanelaSorteio()
        self.janela_sorteio.sorteioRealizado.connect(self.on_sorteio_realizado)
        self.janela_sorteio.showFullScreen()

    def on_sorteio_realizado(self, numero):
        self.numero_sorteado = numero
        self.botao_finalizar.setEnabled(True)

    def finalizar_sorteio_panel(self):
        if not self.numero_sorteado:
            return

        familias = carregar_familias()
        for f in familias:
            if str(f.get("numero")) == str(self.numero_sorteado):
                f["sorteado"] = True
                break

        salvar_familias(familias)
        self.numero_sorteado = None
        self.botao_finalizar.setEnabled(False)

        if self.janela_sorteio:
            self.janela_sorteio.close()

        self.atualizar_galeria()

    def abrir_edicao_familia(self, familia):
        self.janela_edicao = JanelaEditarFamilia(familia, self.atualizar_galeria)
        self.janela_edicao.show()

def iniciar_painel():
    app = QApplication(sys.argv)
    painel = PainelPrincipal()
    sys.exit(app.exec())
