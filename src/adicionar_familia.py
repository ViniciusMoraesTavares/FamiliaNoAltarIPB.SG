from PySide6.QtCore import Signal, Qt  
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PySide6.QtGui import QFont
import os
import json
import shutil
from uuid import uuid4

FOTOS_PATH = "imagens/familias"
DADOS_PATH = "dados/familias.json"

class JanelaAdicionarFamilia(QWidget):
    familia_adicionada = Signal()  

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adicionar Família")
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                color: #3D6D43;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 2px solid #3D6D43;
                border-radius: 8px;
                background-color: #F1F1F1;
            }
            QPushButton {
                padding: 10px;
                background-color: #3D6D43;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #72A06E;
            }
            QPushButton:pressed {
                background-color: #2F4F28;
            }
            QFileDialog {
                font-size: 14px;
                color: #3D6D43;
            }
        """)
        self.resize(400, 250)
        
        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Título da janela
        self.title = QLabel("Adicionar Nova Família")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setStyleSheet("color: #3D6D43;")
        self.layout.addWidget(self.title)

        # Campo para o nome da família
        self.label_nome = QLabel("Nome da Família:")
        self.input_nome = QLineEdit()
        self.layout.addWidget(self.label_nome)
        self.layout.addWidget(self.input_nome)

        # Botão para escolher a foto
        self.botao_escolher_foto = QPushButton("Escolher Foto")
        self.botao_escolher_foto.clicked.connect(self.escolher_foto)
        self.layout.addWidget(self.botao_escolher_foto)

        # Botão para salvar a família
        self.botao_salvar = QPushButton("Salvar Família")
        self.botao_salvar.clicked.connect(self.salvar_familia)
        self.layout.addWidget(self.botao_salvar)

        self.caminho_foto = None

    def escolher_foto(self):
        file_dialog = QFileDialog()
        caminho, _ = file_dialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if caminho:
            self.caminho_foto = caminho
            QMessageBox.information(self, "Foto Selecionada", "Foto selecionada com sucesso!")

    def salvar_familia(self):
        nome_base = self.input_nome.text().strip()
        nome = f"Família {nome_base}"

        if not nome or not self.caminho_foto:
            QMessageBox.warning(self, "Erro", "Por favor, preencha o nome e escolha uma foto.")
            return

        # Criar novo ID
        if os.path.exists(DADOS_PATH):
            with open(DADOS_PATH, "r", encoding="utf-8") as f:
                familias = json.load(f)
        else:
            familias = []

        novo_id = max([f["id"] for f in familias], default=0) + 1
        numero = max([f["numero"] for f in familias], default=0) + 1

        # Salvar a imagem na pasta
        extensao = os.path.splitext(self.caminho_foto)[-1]
        novo_nome_arquivo = f"{uuid4().hex[:8]}{extensao}"
        caminho_destino = os.path.join(FOTOS_PATH, novo_nome_arquivo)
        shutil.copy2(self.caminho_foto, caminho_destino)

        nova_familia = {
            "id": novo_id,
            "numero": numero,
            "nome": nome,
            "foto": caminho_destino.replace("\\", "/"),
            "sorteado": False
        }

        familias.append(nova_familia)

        with open(DADOS_PATH, "w", encoding="utf-8") as f:
            json.dump(familias, f, indent=4, ensure_ascii=False)

        # Emite o sinal para notificar que a família foi adicionada
        self.familia_adicionada.emit()

        QMessageBox.information(self, "Sucesso", f"Família '{nome}' adicionada com sucesso!")
        self.close()
