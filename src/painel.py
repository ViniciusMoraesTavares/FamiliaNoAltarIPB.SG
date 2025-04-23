from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QGroupBox,
    QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
import sys, os, random

from src.adicionar_familia    import JanelaAdicionarFamilia
from src.sorteio_tela          import JanelaSorteio
from src.editar_familia        import JanelaEditarFamilia
from src.janela_confirmacao    import JanelaConfirmacao
from src.utils                 import carregar_familias, salvar_familias
from src.filtro_familias       import nao_sorteadas, sorteadas, buscar
from src.utils_familias import contar_familias
from src.utils_sorteio import salvar_sorteio
from src.resetar import resetar_sorteio


class PainelPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Família no Altar - Painel")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowMinMaxButtonsHint |
            Qt.WindowCloseButtonHint
        )

        self.filtro_atual   = "todas"
        self.termo_pesquisa = ""

        self.janela_adicionar = JanelaAdicionarFamilia()
        self.janela_adicionar.familia_adicionada.connect(self._on_nova_familia)
        self.janela_sorteio   = None
        self.numero_sorteado  = None

        self.init_ui()
        self.showMaximized()

    def _on_nova_familia(self):
        self.filtro_atual = "todas"
        self.search_input.clear()
        self.atualizar_galeria()    

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        titulo = QLabel("Família no Altar - IPB.SG")
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
        self.btn_resetar.clicked.connect(self.resetar_sorteio_callback)
        self.btn_resetar.setStyleSheet(self.estilo_botao_principal())
        self.btn_resetar.setVisible(False)

        botoes_layout.addWidget(btn_adicionar)
        botoes_layout.addWidget(btn_sorteio)
        botoes_layout.addWidget(self.botao_finalizar)
        botoes_layout.addWidget(self.btn_resetar)

        layout.addLayout(botoes_layout)

        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)

        btn_todas     = QPushButton("Todas")
        btn_nao       = QPushButton("Não Sorteadas")
        btn_sorteadas = QPushButton("Sorteadas")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Pesquisar por nome ou número…")

        self.label_total = QLabel()
        self.label_total.setText(f"Total de Famílias: {contar_familias()}")
        self.label_total.setStyleSheet("font-size: 16px; color: #333;")

        for w in (btn_todas, btn_nao, btn_sorteadas, self.search_input, self.label_total):
            filtros_layout.addWidget(w)

        btn_todas.clicked.connect(lambda: self.atualizar_filtro("todas"))
        btn_nao.clicked.connect(lambda: self.atualizar_filtro("nao_sorteadas"))
        btn_sorteadas.clicked.connect(lambda: self.atualizar_filtro("sorteadas"))
        self.search_input.textChanged.connect(self.atualizar_busca)

        layout.addLayout(filtros_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        layout.addWidget(self.scroll_area)

        self.atualizar_galeria()

    def resetar_sorteio_callback(self):
        resetar_sorteio()  # Chama a função do módulo resetar.py
        self.atualizar_galeria()  # Atualiza a galeria após resetar
        self.botao_finalizar.setEnabled(False)  # Desabilita o botão de finalizar sorteio
        self.numero_sorteado = None  # Reseta o número sorteado
        self.verificar_reset_necessario()  # Verifica se o botão de resetar deve ser exibido
        

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

    def atualizar_filtro(self, filtro):
        self.filtro_atual = filtro
        self.atualizar_galeria()

    def atualizar_busca(self, texto):
        self.termo_pesquisa = texto
        self.atualizar_galeria()

    def atualizar_galeria(self):
        familias = carregar_familias()

        if self.filtro_atual == "nao_sorteadas":
            familias = nao_sorteadas(familias)
        elif self.filtro_atual == "sorteadas":
            familias = sorteadas(familias)

        familias = buscar(familias, self.termo_pesquisa)

        grupo = QGroupBox("")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 20px;
                color: #2E7D32;
                margin-top: 5px;
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

        self.label_total.setText(f"Total de Famílias: {contar_familias()}")

    def verificar_reset_necessario(self):
        familias = carregar_familias()
        todas = all(f.get("sorteado", False) for f in familias)
        self.btn_resetar.setVisible(todas)

    def criar_card_familia(self, familia):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        img_label = QLabel()
        caminho = familia.get("foto", "")
        if os.path.exists(caminho):
            pix = QPixmap(caminho).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(pix)
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

        status = "✅ Sorteado" if familia.get("sorteado") else "⏳ Aguardando"
        status_label = QLabel(status)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(
            "color: green;" if familia.get("sorteado") else "color: #888; font-style: italic;"
        )

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

        excluir_btn = QPushButton("🗑️ Excluir")
        excluir_btn.setStyleSheet("""
            QPushButton {
                background-color: #E57373;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #EF5350;
            }
        """)
        excluir_btn.clicked.connect(lambda: self.excluir_familia(familia))

        for w in (img_label, nome_label, numero_label, status_label, editar_btn, excluir_btn):
            layout.addWidget(w)

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
        self.janela_sorteio.show()
        self.botao_finalizar.setEnabled(True)

    def armazenar_sorteio_temporario(self, numero):
        self.numero_sorteado = numero
    
    def on_sorteio_realizado(self, numero):
        self.numero_sorteado = numero
        self.botao_finalizar.setEnabled(True)

    def finalizar_sorteio_panel(self):
        if not self.numero_sorteado:
            return

        familias = carregar_familias()
        familia_sorteada = next((f for f in familias if str(f.get("numero")) == str(self.numero_sorteado)), None)

        if familia_sorteada:
            familia_sorteada["sorteado"] = True
            salvar_familias(familias)

            salvar_sorteio(self.numero_sorteado)

            self.numero_sorteado = None
            self.botao_finalizar.setEnabled(False)

            if self.janela_sorteio:
                self.janela_sorteio.close()

            self.atualizar_galeria()


    def abrir_edicao_familia(self, familia):
        self.janela_edicao = JanelaEditarFamilia(familia, self.atualizar_galeria)
        self.janela_edicao.show()

    def excluir_familia(self, familia):
        texto = f"Tem certeza que deseja\nexcluir a família '{familia['nome']}'?"
        msg_sucesso = f"Família '{familia['nome']}' removida com sucesso!"
        dlg = JanelaConfirmacao(texto, parent=self, info_text=msg_sucesso)
        dlg.confirmado.connect(lambda: self._executar_exclusao(familia))
        dlg.show()

    def _executar_exclusao(self, familia):
        familias = carregar_familias()
        familias = [f for f in familias if f["numero"] != familia["numero"]]
        salvar_familias(familias)
        self.atualizar_galeria()

def iniciar_painel():
    app = QApplication(sys.argv)
    painel = PainelPrincipal()
    sys.exit(app.exec())
