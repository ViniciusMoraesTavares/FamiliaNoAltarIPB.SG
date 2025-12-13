from PySide6.QtCore import Signal, Qt  
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PySide6.QtGui import QFont
import os
from src.data_manager import DataManager

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
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("Adicionar Nova Família")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setStyleSheet("color: #3D6D43;")
        self.layout.addWidget(self.title)

        self.label_nome = QLabel("Nome da Família:")
        self.input_nome = QLineEdit()
        self.layout.addWidget(self.label_nome)
        self.layout.addWidget(self.input_nome)

        self.botao_escolher_foto = QPushButton("Escolher Foto")
        self.botao_escolher_foto.clicked.connect(self.escolher_foto)
        self.layout.addWidget(self.botao_escolher_foto)

        self.botao_salvar = QPushButton("Salvar Família")
        self.botao_salvar.clicked.connect(self.salvar_familia)
        self.layout.addWidget(self.botao_salvar)

        self.caminho_foto = None
        self.data_manager = DataManager()

    def escolher_foto(self):
        file_dialog = QFileDialog()
        caminho, _ = file_dialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if caminho:
            self.caminho_foto = caminho
            QMessageBox.information(self, "Foto Selecionada", "Foto selecionada com sucesso!")

    def salvar_familia(self):
        nome = self.input_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Erro", "Informe o nome da família.")
            return
        if not self.caminho_foto:
            QMessageBox.warning(self, "Erro", "Escolha uma foto válida (.png, .jpg, .jpeg).")
            return
        ok = self.data_manager.adicionar_familia(nome, self.caminho_foto)
        if not ok:
            QMessageBox.warning(self, "Erro", "Não foi possível adicionar a família. Verifique os dados.")
            return
        QMessageBox.information(self, "Sucesso", f"Família '{nome}' adicionada com sucesso!")
        self.familia_adicionada.emit()
        self.close()
